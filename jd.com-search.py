from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os

# 指定关键词
key=["台式机", "工作站", "电脑"]

# 指定价格区间
maxPrice=str(17000)
minPrice=str(10000)



################################################
ext=".txt"
fName=None
################################################
url_base="https://search.jd.com/search"
url_good="https://item.jd.com/"
################################################
os.system("mode con cols=1500 lines=20")
os.system("TITLE 保持浏览器窗口最大化")
def checkDuplicate(item, items):
    for one in items:
        if one.find(item)>=0:
            return True
    return False
    
def delCRLF(string):
    temp = string
    temp = temp.replace("\r", "")
    temp = temp.replace("\n", "")
    return temp

def getRecords(fName):
    fContent=[]
    # 读取已存在的文件
    if os.path.exists(fName):
        f = open(fName, 'r')
        fContent = f.readlines()
        f.close()
        print("已记录 "+str(len(fContent))+" 条商品信息。")
    return fContent
################################################
def search(keyword, min_price, max_price, psort):
    url_visit=url_base
    # print(url_visit)
    fContent = getRecords(fName)
    # 构建搜索地址
    if keyword != "":
        url_visit+="?keyword="+keyword
        
    wq=keyword
    if psort!="":
        url_visit+="&psort="+psort

    if wq!="":
        url_visit+="&wq="+wq

    ev="exprice_"+str(min_price)+"-"+str(max_price)+""
    if ev!="":
        url_visit+="&ev="+ev

    condition="10000"
    
    cur_page=0
    tot_page=1
    total_goods_in_condition=0
    # 初始化环境
    print("初始化环境",end='\r')
    br = webdriver.Firefox()
    br.maximize_window()
    sleep(1)
    # br.minimize_window()
    # 打开页面
    print("打开页面\t",end='\r')
    br.get(url_visit)
    print("等待加载完毕",end='\r')
    # 打开需要写入的文件
    f = open(fName, "w")
    f.write("#################"+keyword+"##############################\r")
    while int(cur_page)<int(tot_page):
        try:
            # 等待加载完毕
            WebDriverWait(br, 50).until(EC.presence_of_element_located((By.ID,"J_resCount")))
            WebDriverWait(br, 50).until(EC.presence_of_element_located((By.ID,"J_goodsList")))
        except selenium.common.exceptions.TimeoutException:
            print("Err selenium timeout\r")
            continue
        except:
            continue
        
        # 统计商品数量以及页数
        total_num = br.find_element_by_id("J_resCount").text
        # print("共搜索到 "+total_num+" 个商品")
        topPage=None
        topPage = br.find_element_by_id("J_topPage")
        cur_page = topPage.find_element_by_tag_name("b").text
        tot_page = topPage.find_element_by_tag_name("i").text
        
        #滚动到页面底部
        br.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")
        sleep(1)
        br.execute_script("window.scrollTo(0, document.body.scrollHeight*2/4);")
        sleep(1)
        br.execute_script("window.scrollTo(0, document.body.scrollHeight*3/4);")
        sleep(1)
        br.execute_script("window.scrollTo(0, document.body.scrollHeight*4/4);")
        sleep(1)
        # 列出商品地址
        goods=None
        goods = br.find_element_by_id("J_goodsList").find_elements_by_tag_name("li")
      
        if len(goods)>0:
            for good in goods:
                data_sku = good.get_attribute("data-sku")
                if data_sku.find(condition)>=0:
                    total_goods_in_condition+=1
                    price = good.find_element_by_class_name("p-price").find_element_by_tag_name("i").text
                    # 如果之前有记录，则跳过该商品，不再重复记录。
                    header=""
                    goodName=""
                    goodName = good.find_element_by_class_name("p-name-type-2").find_element_by_tag_name("em").text
                    goodName = delCRLF(goodName)
                    haveGoods=""
                    try:
                        haveGoods = good.find_element_by_class_name("p-stock").text
                    except:
                        pass
                    if checkDuplicate(data_sku, fContent) is True:
                        # print("#\t"+data_sku+"\t"+price+"\t"+goodName)
                        header+="#"
                    else:
                        try:
                            f.write(url_good+data_sku+".html"+"\t"+price+"\t"+haveGoods+"\t"+goodName+"\r")
                        except UnicodeEncodeError:
                            print("Err UnicodeEncodeError")
                            f.write(url_good+data_sku+".html"+"\t"+price+"\r"+haveGoods)
                        except:
                            print("Err UnicodeEncodeError+")
                        f.flush()
                    print(header+"\t"+data_sku+"\t"+price+"\t"+haveGoods+"\t"+goodName)
                else:
                    # print("\t"+data_sku)
                    pass
                data_sku=None
                good=None
        else:
            print("该页面，未找到商品。")
        print("共"+tot_page+"页，当前第 "+cur_page+" 页，当前页面 "+str(len(goods))+" 个商品，共找到 "+str(total_goods_in_condition)+" 个符合要求的商品。",end='\r')
        # 进入下一页
        try:
            WebDriverWait(br, 5).until(EC.presence_of_element_located((By.ID,"J_bottomPage")))
            br.find_element_by_id("J_bottomPage").find_element_by_class_name("pn-next").click()
        except:
            print("\n没有下一页了。")
        sleep(1)

    f.close()
    print("\n搜索完毕，符合条件的商品 "+str(total_goods_in_condition)+" 件")

    #br.refresh() #刷新页面
    br.close() # 关闭浏览器
    br.quit() # 退出selenium


fName="searchResult"+"-["+maxPrice+"-"+minPrice+"]"+ext
for k in key:
    print("\t\t关键词："+k+"\r\n")
    os.system("TITLE 保持浏览器窗口最大化 "+k)
    search(k, minPrice, maxPrice, "1")
    print("############################################################")

