#-*- coding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import time,datetime
import json
import random
import threading
from multiprocessing import Process,Queue
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


shopList=Queue()
completeCount=0 

def getItems(shop) :   
    ua=UserAgent()
    ipList=["112.217.199.122:55872","121.139.218.165:31409","183.111.26.15:8080","211.203.234.141:8080","222.121.116.26:47314"
    ,"115.21.163.39:8888","1.215.70.130:44072","210.107.78.173:3128","112.168.11.170:808","222.121.116.26:55149","175.125.216.117:8080"
    ,"211.244.224.130:8080","106.10.55.212:3128","119.192.195.83:8080","213.109.133.156:8080","23.237.173.102:3128","216.198.188.26:51068"
    ,"209.212.33.99:8080","64.20.33.202:8080","35.245.208.185:3128"
    ] 
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
            req=requests.get(url,headers=headers,proxies=proxies,timeout=1)
            source = req.text
            bs=BeautifulSoup(source,"html.parser")
            print(bs.find("title").text)
            if(bs.find("title").text == "서비스 접근 권한이 없습니다 : 네이버쇼핑"):
                raise Exception
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
        
    print(shop[0]+"\t close take "+str(datetime.datetime.now().replace(microsecond=0)-stime)+" get "+str(itemCount)+" items\n")
    file.close()

def getShopList():
    driver = webdriver.PhantomJS()
    url="https://search.shopping.naver.com/mall/mall.nhn"
    driver.get(url)
    element = driver.find_element_by_id('gift_shopn').click()
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
            shopList.put([ss['name'],ss['seq']])
        nextBtn=bs.find("a",{"class":"next"})    
    driver.close()


if __name__ == '__main__':
    stime=datetime.datetime.now().replace(microsecond=0)
    print("start !!"+str(stime))
    gsl=threading.Thread(target=getShopList)
    gsl.start()

    ing=[]
    time.sleep(10)

    while(shopList.qsize()!=0):
        for t in ing:
            if not t.is_alive():
                ing.remove(t)
                completeCount+=1

        if len(ing)<16:
            # threading #
            # t=threading.Thread(target=test,args=(shopList.pop(),))
            # t.start()
            # ing.append(t)
            t=Process(target=getItems,args=(shopList.get(),))
            t.start()
            ing.append(t)
            print(str(completeCount/shopList.qsize())+"% ("+str(completeCount)+"/"+str(shopList.qsize())+") 완료",end="\r")
    print("close!!!"+str(stime-datetime.datetime.now().replace(microsecond=0)))
    input("press Enter")