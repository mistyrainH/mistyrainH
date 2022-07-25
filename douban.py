# -*- coding: utf-8 -*-
# @Time    : 2022-07-20 23:44
# @Author  : hxj
# @File    : 1.py

import urllib
import xlwt
from bs4 import BeautifulSoup
import re
import sqlite3

# 流程：
# 1.爬取网页
# 2.解析数据
# 3.保存数据

def main():
    baseurl = "https://movie.douban.com/top250?start="
    # 1.爬取网页
    datalist = getData(baseurl)
    savepath = ".\\douban_top250.xls"
    # 3.保存数据
    saveData(datalist,savepath)

    askURL("https://movie.douban.com/top250?start=")

#影片链接的规则
findLink = re.compile(r'<a href="(.*?)">')         #创建正则表达式对象，表示规则（字符串）
#影片图片
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)         #.S忽略换行符
#影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
#影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#评价人数
findJudge = re.compile(r'<span>(\d*)人评价</span>')
#找到概况
findInq =re.compile(r'<span class="inq">(.*)</span>')
#找到影片的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)

# 1.爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0,10):           #获取页面信息的函数，10次
        url = baseurl + str(i*25)
        html = askURL(url)      #保存获取到的网页源码

        # 2.逐一解析数据
        soup = BeautifulSoup(html,"html.parser")
        for item in soup.find_all('div',class_="item"):         #查找符合要求的字符串
            data = []       #保存一部电影的所有信息
            item = str(item)
            # print(item)
            # break
            #影片详情的链接
            link = re.findall(findLink,item)[0]         #re库通过正则表达式查找制定的字符串
            data.append(link)                           #添加链接

            imgSrc = re.findall(findImgSrc,item)
            # print(str(imgSrc))
            data.append(imgSrc)                         #添加图片

            titles = re.findall(findTitle,item)         #片名可能有中英文多个
            if len(titles) == 2:
                ctitle = titles[0]                      #添加中国名字
                data.append(ctitle)
                otitle = titles[1].replace("/","")
                data.append(otitle)                     #添加外国名字
            else:
                data.append(titles[0])
                data.append(' ')                        #外国名留空

            rating = re.findall(findRating,item)[0]
            data.append(rating)                         #添加评价分数

            judgeNum = re.findall(findJudge,item)[0]
            data.append(judgeNum)                       #添加评价人数

            inq = re.findall(findInq,item)
            if len(inq) != 0:
                inq = inq[0].replace("。","")            #去掉句号
                data.append(inq)                        #添加概述
            else:
                data.append(' ')                        #留空

            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', ' ', bd)     #去掉<br/>
            bd = re.sub('/', ' ', bd)                   #去掉<br/>
            data.append(bd.strip())                     #去掉前后空格

            datalist.append(data)                           #把处理好的一部电影信息放入datalist
    return datalist


#得到指定一个URL的网页内容
def askURL(url):

    #用户代理，告诉服务器，我们是什么类型的机器，模拟浏览器发送信息（本质上告诉浏览器我们可以接受什么类型的信息）
    head = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Mobile Safari/537.36"
    }

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e,"code")
        if hasattr(e, "reason"):
            print(e,"reason")
    return html



# 3.保存数据
def saveData(datalist,savepath):
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)      #创建对象
    sheet = book.add_sheet("豆瓣电影top250",cell_overwrite_ok=True)     #创建工作表，cell_overwrite_ok是覆盖
    col = ("电影详情链接","图片链接","中国名","外国名","评分","评价数","概况","相关信息")
    for i in range(0,8):
        sheet.write(0,i,col[i]) #列名
    for i in range(0,250):
        print(f"第{i+1}条")
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])          #数据

    book.save(savepath)          #保存



if __name__ == "__main__":
    main()
    print("爬取完毕")
