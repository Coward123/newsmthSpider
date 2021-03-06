from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import urllib.parse  
import re, time,os 
import urllib.request  
import sqlite3
from unit.sendMail import sendMail
from unit.getEnv import getEnv
import datetime

class sqliteOS3(object):
    def __init__(self, dataBasePath):
        super().__init__();
        if not os.path.isfile(dataBasePath):
           conn = sqlite3.connect(dataBasePath) 
           cu = conn.cursor()
#           cu.execute("create table newsmth(id integer primary key autoincrement, urlID integer, nameTitle varchar(128) UNIQUE, postTime varchar(128) UNIQUE, sendKey interger)")
           cu.execute("create table newsmth(id integer primary key autoincrement, urlID integer, nameTitle varchar(128), postTime varchar(128), sendKey interger, sendMailKey interger)")
           conn.close()  

        self.dataBasePath = dataBasePath;
#        print(dataBasePath)

    def connectData(self,):
        return sqlite3.connect(self.dataBasePath); 

    def insertData(self, conn, urlID, nameTitle, postTime, sendKey,sendMailKey):
        self.urlID = urlID;
        self.nameTitle = nameTitle;
        self.postTime = postTime;
        self.sendKey = sendKey;
        self.sendMailKey = sendMailKey;

#       print(self.dataBasePath)
        #conn = sqlite3.connect(self.dataBasePath);
        cu = conn.cursor(); 
        cmdLineInsert = "insert into newsmth values((select max(ID) from newsmth)+1," + self.urlID + "," + self.nameTitle + "," + self.postTime + "," + self.sendKey + "," + self.sendMailKey + ")"
        cu.execute(cmdLineInsert)
        conn.commit()

    def closeSqlite3(self, conn):
#        conn = self.connectData();
        conn.close()

    def searchAllSqlite3(self,conn):
        cur = conn.cursor()
        cur.execute('select * from newsmth')
        return (cur.fetchall())

    def searchURLSqlite3(self,conn, urlID):
        cur = conn.cursor()
        try:
            cur.execute("select * from newsmth where urlID=%s" %urlID)
            if len(cur.fetchall()) == 0:
                return True;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchURLSqlite3 error, please check your param! \n")
            return False;

    def searchNameTitleFromSqlite3(self,conn,urlID):
        cur = conn.cursor()
        try:
            cur.execute("select nameTitle from newsmth where urlID=%d" %urlID)
#            print("select nameTitle from newsmth where urlID=%d" %urlID)
            return cur.fetchall();
        except Exception as e:
            print("ERROR: searchNameTitleFromSqlite3 error, please check your param! or Contact with Me\n")
            return False;

    def searchURLIdFromSqlite3(self,conn,sendKey):
        cur = conn.cursor()
        try:
            cur.execute("select urlID from newsmth where sendKey=%d" %sendKey)
            return cur.fetchall();
        except sqlite3.Error as e:
            print("ERROR: searchURLIdFromSqlite3 error, please check your param! \n")
            return False;

    def searchSendMailKeyFromSqlite3(self,conn,sendMailKey):
        cur = conn.cursor()
        try:
            cur.execute("select urlID from newsmth where sendMailKey=%d" %sendMailKey)
            return cur.fetchall();
        except sqlite3.Error as e:
            print("ERROR: searchSendMailKeyFromSqlite3 error, please check your param! \n")
            return False;

    def updateSendKeyValue(self, conn, urlID):
        cur = conn.cursor()
        try:
            cur.execute("UPDATE newsmth SET sendKey = 1 where urlID=%d" %urlID)
            conn.commit()
        except sqlite3.Error as e:
            print("ERROR: updateSendKeyValue error, please check your param! \n")
            conn.rollback()
            return False;

    def updateSendMailKeyValue(self, conn, urlID):
        cur = conn.cursor()
        try:
            cur.execute("UPDATE newsmth SET sendMailKey = 1 where urlID=%d" %urlID)
            conn.commit()
        except sqlite3.Error as e:
            print("ERROR: updateSendMailKeyValue error, please check your param! \n")
            conn.rollback()
            return False;

    def deleteInvalidURLID(self, conn, urlID):
        cur = conn.cursor()
        try:
            cur.execute("delete from newsmth where urlID=%d" %urlID)
            conn.commit()
        except sqlite3.Error as e:
            print("ERROR: deleteInvalidURLID error, please check your param! \n")
            conn.rollback()
            return False;
pUrlValue = 1
class parseUrl(sqliteOS3):
    def __init__(self, URL, dataBasePath):
        sqliteOS3.__init__(self, dataBasePath) 
        headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        opener = urllib.request.build_opener()
        opener.addheaders = [headers]
        try:
            data = opener.open(URL).read()
        except Exception as e:
            print("Error: open url=%s error\n" %URL)
            return False
        self.mainData = data.decode("utf8").split('<div class="sec nav">')[-2].split('class="top"')[-1].split("</a></div></li>")
        self.dataBasePath = dataBasePath

    def getData(self):
        sql = sqliteOS3(self.dataBasePath)
        global pUrlValue 
        conn = sql.connectData()
        pValue = 0
        testKey = ["\u6d4b\u8bd5","QE","test","Test","qa","QA","qe"]
        for i in range(0, len(self.mainData)):
            if self.mainData[i].find("Career_Upgrade") != -1:
                urlLine = self.mainData[i].find('<a href="/article/Career_Upgrade/')
                if self.mainData[i][urlLine:].split('&nbsp;')[0].split('</div><div>')[-1].find(":") != -1:
                    pValue += 1;
                aLine = self.mainData[i][urlLine:].split('&nbsp;')[0].split('</div><div>')[0].find('</a>')
                #title
                for key in range(0,len(testKey)):
                    if ((re.sub('\d\d'+';', '',self.mainData[i][urlLine:].split('&nbsp;')[0].split('</div><div>')[0][:aLine].split('">')[-1]).replace('&#','')).strip()).find(testKey[key]) != -1:
                        titleName = (re.sub('\d\d'+';', '',self.mainData[i][urlLine:].split('&nbsp;')[0].split('</div><div>')[0][:aLine].split('">')[-1]).replace('&#','')).strip()
#                        print(titleName)
                        # urlId
                        urlID = self.mainData[i][urlLine:].split('&nbsp;')[0].split('</div><div>')[0][:aLine].split('">')[0].split('<a href="/article/Career_Upgrade/')[-1]
#                       print(urlID)
                        if self.mainData[i][urlLine:].split('&nbsp;')[0].split('</div><div>')[-1].find(":") != -1:
#                            pValue += 1;
                        #time
                            timePost = time.strftime('%Y-%m-%d',time.localtime(time.time())) + ' ' +self.mainData[i][urlLine:].split('&nbsp;')[0].split('</div><div>')[-1]
                            timePost = "'"+timePost+"'"
#                            print(timePost)
                            titleName ="'" + titleName + "'"

                            if sql.searchURLSqlite3(conn, urlID):
                                sql.insertData(conn, urlID, titleName, timePost, '0', '0')

        sql.closeSqlite3(conn);
        if pValue >= 1:
            pUrlValue += 1

class parseURL:
    def __init__(self, URLID):
        self.urlid = URLID
        super() .__init__();
        headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        opener = urllib.request.build_opener()
        opener.addheaders = [headers]

        URL = "http://www.newsmth.net/nForum/article/Career_Upgrade/"+str(URLID)+"?ajax"
        self.URL = URL
        try:
            data = opener.open(URL).read()
            self.mainUrlData = data.decode("GBK")
        except Exception as e:
            print("Open url:%s is error, please check the URL!~\n" %URL)

    def parseURL(self,):
        keyUrl ="\u6307\u5B9A\u7684\u6587\u7AE0\u4E0D\u5B58\u5728\u6216\u94FE\u63A5\u9519\u8BEF"
        try:
            if (self.mainUrlData.find(keyUrl)) == -1:
                if self.mainUrlData.find('<p>') == -1:
                    print("\n\nThe URL maybe not exist, please check %s \n" %self.URL)
                    return False 
                contextURL = self.mainUrlData.split('<p>')[1].split('FROM')[0].replace('&nbsp;','')
                if contextURL.find('--<br ') != -1:
                    return (contextURL.split('--<br ')[0])
                elif contextURL.find('-- <br ') != -1: 
                    return (contextURL.split('-- <br ')[0])
            else:
                sql = sendMsg().sqlURLID()
                conn = sql.connectData()
                sql.updateSendMailKeyValue(conn, self.urlid);
        except Exception as e:
            print("Open url:%s is error, please check the URL!~\n" %self.URL)
            return False


    def parseContext(self,):
        URLID = sendMsg();
        sql = URLID.sqlURLID()
        conn = sql.connectData()
        parseURLWeb = parseURL(self.urlid)
        if self.parseURL():
           titleName = str(sql.searchNameTitleFromSqlite3(conn,self.urlid)[0]).replace('(','').replace(')','').replace("'","").replace(',',' ')
           urlContxt = parseURLWeb.parseURL().replace('<br />','\n')
#           sql.updateSendKeyValue(conn,self.urlid);
           return (titleName,urlContxt);
        return False

class postMsg(sqliteOS3):
    def __init__(self, dataBasePath):
        sqliteOS3.__init__(self, dataBasePath) 
        sql = sqliteOS3(dataBasePath)
        self.sql = sql
        conn = sql.connectData()
        self.URLIDData = sql.searchURLIdFromSqlite3(conn, 0)
        self.sendMailKeyData = sql.searchSendMailKeyFromSqlite3(conn, 0)
        
    def urlContext(self,):
        return self.URLIDData;
    
    def sqlUrlID(self,):
            return self.sql

    def sendMailData(self,):
        return self.sendMailKeyData

class sendMsg:
    def __init__(self,):
        super().__init__();
        urlDefault = 1
        dataBasePath = "/home/licaijun/newsmth.db"
        self.dataBasePath = dataBasePath
        while(1):
            url="http://m.newsmth.net/board/Career_Upgrade?p="+str(urlDefault)+"?ajax"  
            parseurl = parseUrl(url, dataBasePath)
            parseurl.getData()
            if pUrlValue > urlDefault:
                urlDefault = pUrlValue;
            else:
                break;
        
    def sendMsg(self,):
        post = postMsg(self.dataBasePath)
        return post.urlContext()

    def sqlURLID(self,):
        post = postMsg(self.dataBasePath)
        return post.sqlUrlID()

    def sendMailData(self,):
        post = postMsg(self.dataBasePath)
        return post.sendMailData()

global URLIDDataWebdriver

class Untitled(unittest.TestCase):
    def setUp(self):
#        self.driver = webdriver.Firefox()
        self.driver = webdriver.PhantomJS(executable_path='/usr/bin/phantomjs')
        self.driver.implicitly_wait(30)
#        self.base_url = "http://www.newsmth.net"
        self.base_url = "http://m.newsmth.net"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_untitled(self):
        driver = self.driver
#        driver.get("http://www.newsmth.net")
#        driver.find_element_by_id("id").clear()
#        print(getEnv("newsmthID").getEnv())
#        driver.find_element_by_id("id").send_keys(getEnv("newsmthID").getEnv())
#        driver.find_element_by_id("pwd").clear()
#        print(getEnv("newsmthPW").getEnv())
#        driver.find_element_by_id("pwd").send_keys(getEnv("newsmthPW").getEnv())
#        driver.find_element_by_id("b_login").click()

        driver.get("http://m.newsmth.net")
        driver.find_element_by_name("id").clear()
        driver.find_element_by_name("id").send_keys(getEnv("newsmthID").getEnv())
        driver.find_element_by_name("passwd").clear()
        driver.find_element_by_name("passwd").send_keys(getEnv("newsmthPW").getEnv())
        driver.find_element_by_css_selector("input.btn").click()
#        driver.find_element_by_name("b_login").click()
        time.sleep(3)

        sql = sendMsg().sqlURLID()
        conn = sql.connectData()
        for i in range(0, len(URLIDDataWebdriver)):
            URLID = URLIDDataWebdriver[i][0]
            parseURLWeb = parseURL(URLID)
            if parseURLWeb.parseContext():
                (titleName,urlContxt)=parseURLWeb.parseContext()
#                driver.get("http://www.newsmth.net" + "/nForum/article/Test/post")
                print(titleName)
                driver.get("http://www.newsmth.net" + "/nForum/article/SoftwareTesting/post")
                driver.find_element_by_id("post_subject").clear()
                driver.find_element_by_id("post_subject").send_keys(titleName)
                driver.find_element_by_id("post_content").click()
                driver.find_element_by_id("post_content").clear()
                driver.find_element_by_id("post_content").send_keys(urlContxt)
                driver.find_element_by_css_selector("input.button").click()
                time.sleep(20)
                sql.updateSendKeyValue(conn,URLID);

#        driver.find_element_by_id("u_login_out").click()
    
    def is_element_present(self, how, what):
        try: 
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: 
            return False
        return True
    
    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e: 
            return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

class mailList:
    def __init__(self,file):
        self.mailList = []
        try:
            fd = open(file)
            line = fd.readline()
            while line:
                self.mailList.append(line.strip())
                line = fd.readline()
            fd.close()
        except Exception as e:
            print("Error:open configure file:%s error!\n" %file)
            fd.close()
            return False

    def getmailList(self,):
        return self.mailList

class setEnv:
    def __init__(self,file):
        super().__init__()
        try:
            fd = open(file)
            line = fd.readline()
            while line:
                line=line.split('=')
                os.putenv(line[0],line[1])
                line = fd.readline()
        except Exception as e:
            print("Error:open configure file:%s error!\n" %file)
            return False
        finally:
            fd.close()

if __name__ == "__main__":
    setEnv("configure/login.txt")
    mList = mailList("configure/mailList.txt") 

    sql = sendMsg().sqlURLID()
    conn = sql.connectData()

    URLID = sendMsg();
    URLIDDataWebdriver = URLID.sendMsg()
    sendMailData = URLID.sendMailData()

    if len(sendMailData) > 0:
        for i in range(0, len(sendMailData)):
            URLID = sendMailData[i][0]
            parseURLWeb = parseURL(URLID)
            if parseURLWeb.parseContext():
                (titleName,urlContxt)=parseURLWeb.parseContext()
                print("sendMail:%s" %titleName)
                sendmail = sendMail(titleName, urlContxt, mList.getmailList())
                sendmail.sendmail();
                print("start update sendMailKey value")
                sql.updateSendMailKeyValue(conn,URLID);

    weekday = datetime.datetime.now().weekday() 

    if len(URLIDDataWebdriver) > 0:
        unittest.main()
