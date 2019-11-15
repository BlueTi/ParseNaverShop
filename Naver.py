#-*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import time,datetime
import json
import random
import threading
from multiprocessing import Pool
from urllib import parse
import requests
import concurrent.futures
from fake_useragent import UserAgent

# SET MOBILE #
# mobile_emulation = {
#     "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
#     "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }
# chrome_options = Options()
# chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
#driver = webdriver.Chrome(chrome_options = chrome_options)
ua=UserAgent()
ipList=["141.223.132.163:80","222.112.240.154:80","121.165.92.44:8080","175.125.216.117:8080","112.218.215.140:8080"
    ,"112.168.11.170:808","222.121.116.26:55149","211.244.224.130:8080","183.111.26.15:8080","119.192.179.46:45447"
    ,"222.121.116.26:57074","118.176.244.226:8080","210.107.78.173:3128","222.112.240.154:80","222.112.240.141:80"
    ,"121.139.218.165:31409","119.192.179.46:31990","183.111.26.15:8080","103.211.76.5:8080","27.116.51.115:8080"
    ,"36.92.22.70:8080","103.248.198.37:8080","178.77.238.2:8080","45.32.107.74:8080","50.235.28.146:3128","198.11.178.14:8080"
    ]
shopList=[]
completeCount=0 

def test(shop) :    
    file = open("data/"+shop[0]+".txt","w",encoding="utf-8")
    stime=datetime.datetime.now().replace(microsecond=0)
    pageCount=1
    itemCount=0
    nextBtn=1
    while nextBtn!=None:    
        proxy_index = random.randint(0, len(ipList) - 1)
        proxies={"https":ipList[proxy_index]}
        url="https://search.shopping.naver.com/search/all.nhn?origQuery="+str(parse.quote(shop[0]))+"&mall="+shop[1]+"&pagingIndex="+str(pageCount)+"&pagingSize=80&viewType=list&sort=rel&frm=NVSHPAG&query="+str(parse.quote(shop[0]))
        headers={"User-Agent":ua.random}
        try:
            req=requests.get(url,headers=headers,proxies=proxies)
            source = req.text
            bs=BeautifulSoup(source,"html.parser",from_encoding="euc-kr")
            items=bs.find_all("li",{"class":"_itemSection"})
            for item in items:
                itemCount+=1
                file.write(shop[0]+"("+shop[1]+"):"+item.find("div",{"class","tit"}).text.replace("\n","")+","+item.find("span",{"class":"price"}).text.replace("\n","").replace("가격비교","")+",")
                if(len(item.find_all("a",{"class":"graph"}))>0):
                    for etc in item.find_all("a",{"class":"graph"}):
                        file.write(etc.text.replace("\n",""))
                file.write("\n")
            nextBtn=bs.find("a",{"class":"next"})
            pageCount+=1        
            req.close()
        except:
            nextBtn=1
        
    print(shop[0]+"\t close take "+str(datetime.datetime.now().replace(microsecond=0)-stime)+" get "+str(itemCount)+" items")
    global completeCount
    completeCount+=1
    file.close()

def getShopList(driver):
    nextBtn=1
    pageCount=0
    while(nextBtn!=None):
        pageCount+=1
        driver.execute_script("mall.changePage("+str(pageCount)+")")
        time.sleep(1)
        source = driver.page_source
        bs = BeautifulSoup(source,"html.parser",from_encoding="euc-kr")
        tds = bs.find_all("td",{"class":"mall"})
        for d in tds:
            aTag=d.find_all("a")[1]
            start=aTag['onfocus'].find("{")
            end=aTag['onfocus'].rfind("}")+1
            atr=aTag['onfocus'][start:end].replace("'",'"')
            ss=json.loads(atr)
            shopList.append([ss['name'],ss['seq']])
        nextBtn=bs.find("a",{"class":"next"})    
    driver.close()
 
stime=datetime.datetime.now().replace(microsecond=0)
print("start !!"+str(stime))
driver = webdriver.PhantomJS()
url="https://search.shopping.naver.com/mall/mall.nhn"
driver.get(url)
element = driver.find_element_by_id('gift_shopn').click()
time.sleep(1)
gsl=threading.Thread(target=getShopList,args=(driver,))
gsl.start()

ing=[]
time.sleep(10)
pool=Pool(processes=16)
while(len(shopList)!=0):
    for t in ing:
        if not t.isAlive():
            ing.remove(t)
    if len(ing)<16:
        # t=threading.Thread(target=test,args=(shopList.pop(),))
        # t.start()
        pool.map(test,(shopList.pop(),))
        print(str(completeCount/len(shopList))+"% ("+str(completeCount)+"/"+str(len(shopList))+") 완료",end="\r")
        #ing.append(t)
print("close!!!"+str(stime-datetime.datetime.now().replace(microsecond=0)))
input("press Enter")