
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.webdriver.common.proxy import Proxy
from selenium.common.exceptions import TimeoutException
from time import sleep
from os import system
import logging
import queue
import threading
import xlsxwriter

readed = []  # readed user-agent bilgisi tutucak
linkDetails = queue.Queue()

logging.basicConfig(filename='AppLog.log', level=logging.WARNING)
logging.getLogger()


def exceptLog(msg):
    try:
        logging.exception(msg)
        return True
    except Exception as e:
        logging.exception(e)
    return False

# User-Agent Dosyamı okuyorum
def userAgentRead():
    try:
        with open("user-agent.txt", "r", encoding="utf-8") as file:
            reads = file.readlines()
            for read in reads:
                readed.append(read.strip())
            return True
    except Exception as e:
        exceptLog(e)
    return False


def getUserAgent():
    if len(readed) > 1:
        userAgent = readed[0]
        readed.remove(userAgent)
    else:
        userAgentRead()
        userAgent = readed[0]
        readed.remove(userAgent)
    return userAgent

def getProfile():
    if not len(readed) > 0:
        userAgentRead()
    useragent = getUserAgent()
    profile = webdriver.FirefoxProfile()
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.set_headless()
    profile.set_preference("general.useragent.override", useragent)    
    profile.update_preferences()
    return (profile,fireFoxOptions)

def trySelectCssSelector(wait,selector,elseSelector=False,log=True):
    try:
        data = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,selector)))
        return data
    except Exception as e:        
        print(e)
        if log:
            exceptLog(e)
        try:
            data = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,elseSelect)))
            return data
        except Exception as e:
            return None
        
def trySelectCssSelectorAll(wait,selector,elseSelector=False,log=True):
    # print(selector,elseSelector)
    try:
        data = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,selector)))
        return data
    except Exception as e:        
        print(e)
        if log:
            exceptLog(e)
            
        if elseSelector:
            try:
                data = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,elseSelector)))
                return data
            except Exception as e:
                return None

def getPageDetails(link,count,count2):
    try:
        firefoxProfile,firefoxOption = getProfile()
        browser = webdriver.Firefox(firefox_profile=firefoxProfile,firefox_options=firefoxOption)
        browser.get(link)
        wait = WebDriverWait(browser, 2)
        #Fuarın Adı Ülke Şehir	Adres	Sektör	Business Segment Certificates Products	HS Codes
        flag = []
        categories = ""
        adres = ""
        hscode = ""
        businessSegment = ""
        certificate = ""
        product = ""
        keyword = ""
        
        title = trySelectCssSelector(wait,".company-detail-name h1").text
        categoriesText = trySelectCssSelectorAll(wait,".detail-right-ctagories-box p")
        adresText = trySelectCssSelectorAll(wait,".companies-detail-right-address p")
        businessSegmentText = trySelectCssSelectorAll(wait,".companies-detail-right-Business-Segment p")
        certificatesText = trySelectCssSelectorAll(wait,".companies-detail-right-Certificates a",".companies-detail-right-Certificates p")
        hscodeText = trySelectCssSelectorAll(wait,".companies-detail-right-gtip-code a",".companies-detail-right-gtip-code p")
        try:
            trySelectCssSelector(wait,"#btnReadMoreKeywords").click()
        except Exception as e:
            print(e)
        keywordText = trySelectCssSelectorAll(wait,".keyword-item")
        productLinks = trySelectCssSelectorAll(wait,".product-preview-item a")

        #title category  adres  businessSegment certificate product  hscode  keyword

        flag.append(title)
        if categoriesText:
            for category in categoriesText:
                categories += "," + category.text.strip()
            flag.append(categories[1:])
                
        if adresText:
            for adress in adresText:
                adres += "," + adress.text.strip()
            flag.append(adres[1:])

        if businessSegmentText:
            for businessSegments in businessSegmentText:
                businessSegment += "," +  businessSegments.text.strip()
            flag.append(businessSegment[1:])

        if certificatesText:
            for certificates in certificatesText:
                certificate += "," + certificates.text.strip()
            flag.append(certificate[1:])

        if productLinks:
            for products in productLinks:
                product += "," + products.get_attribute("href")
            flag.append(product[1:])

        if hscodeText:
            for hscodes in hscodeText:
                hscode += "," + hscodes.text.strip()
            flag.append(hscode[1:])

        if keywordText:
            for keywords in keywordText:
                keyword += "," + keywords.text.strip()
            flag.append(keyword[1:])

        print(flag,len(flag)," \t",str(count) + " /" + str(count2) )
        linkDetails.put(flag)
    except Exception as e:
        print(e)
        exceptLog(e)
    finally:
        browser.close()
    
   

def main():
    firefoxProfile,firefoxOption = getProfile()
    browser = webdriver.Firefox(firefox_profile=firefoxProfile,firefox_options=firefoxOption)
    print("Browser Açılyor.")
    sleep(2)
    browser.get("https://www.turkishexporter.com.tr/en/companies/turkey/")
    # browserın tam açılmasını bekliyorum
    # website yüklendikten belirli bir süre sonra işlem yapmamı imkan sağlar.
    print("2 saniye bekleyiniz.")
    sleep(2)
    wait = WebDriverWait(browser, 5)
    links = queue.Queue()    
    try:
        # 123736 exporters are listed on 12374 pages.

        pageCount = wait.until(EC.presence_of_element_located((By.CLASS_NAME,"form-text"))).text.split()[-2]
        print("PageCount : ",pageCount)
        # company-detayil-link
        for page in range(1,int(1)+1):
            browser.get("https://www.turkishexporter.com.tr/en/companies/turkey/?page={}".format(page))                  
            sleep(3)
            if (browser.title.strip().lower() == "error"):
                break
            containerLinks = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"company-detayil-link")))
            for container in containerLinks:
                print(container.get_attribute("href")," ",page," ",links.qsize())
                links.put(container.get_attribute("href"))
        
        
        browser.close()
        linkDetails.put(["title","category","adres","businessSegment","certificate","product","hscode","keyword"])

        count = 0
        count2 = 0
        totalSize = links.qsize()


        for item in range(links.qsize()):
            print("browser açılıyor hocam")
            link = links.get()
            if threading.active_count() != 3:
                x = threading.Thread(target=getPageDetails, args=(link,totalSize,count2,))
                x.start()
            sleep(3)
            count2 += 1
            print(threading.active_count())
            print("linkdetay : ",linkDetails.qsize()," totalSize : ",totalSize)
        # print("linkdetay : ",linkDetails.qsize()," totalSize : ",totalSize)


        # for item in range(links.qsize()):
            # print("Browser Açılyor.")
            # print(count2)
            # link = links.get()
            # getPageDetails(link, totalSize, count2)
            # count2 += 1
            # print("linkdetay : ",linkDetails.qsize()," totalSize : ",totalSize)
            # x = threading.Thread(target=getPageDetails, args=(link,totalSize,count2,))
            # x.start()
            # count +=1
            # if count == 4:
            #     sleep(45)
            #     count = 0
            #     print("linkdetay : ",linkDetails.qsize()," totalSize : ",totalSize)
            # count2 += 1 

        while True:
            print(linkDetails.qsize())
            if (linkDetails.qsize() == totalSize):
                print("excel yazmaya başladı !!!".upper())
                #title category  adres  businessSegment certificate product  hscode  keyword
                #excel işlemine başla
                workbook = xlsxwriter.Workbook('Data.xlsx') 
                workSheet = workbook.add_worksheet()
                row = 0
                col = 0
        
                for item in range(linkDetails.qsize()):
                    detail = linkDetails.get()
                    if len(detail) == 8:
                        workSheet.write(row,col,detail[0])
                        workSheet.write(row,col + 1,detail[1])
                        workSheet.write(row,col + 2,detail[2])
                        workSheet.write(row,col + 3,detail[3])
                        workSheet.write(row,col + 4,detail[4])
                        workSheet.write(row,col + 5,detail[5])
                        workSheet.write(row,col + 6,detail[6])
                        workSheet.write(row,col + 7,detail[7])
                        row += 1

                workbook.close()
                print("excel yazma işlemi tamamlandı !!!".upper())
                break
            sleep(30)


    except Exception as e:
        print(e)
        exceptLog(e)
    finally:
        try:
            browser.close()
        except Exception as e:
            pass

if __name__ == "__main__":
    main()

