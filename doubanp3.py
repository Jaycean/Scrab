#!/usr/bin/env python
# -*- coding=utf-8 -*-
import urllib
from urllib import request
import re
import time
from bs4 import BeautifulSoup
from multiprocessing import Pool
from multiprocessing import Manager
import random

def get_html(url, user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0', num_retries=10):
    """支持user-agent并且可以尝试多次爬取数据的爬虫"""
    ##print('Downloading:', url)

    # user-agent设置
    headers = {'User-agent': user_agent}
    req = request.Request(url, headers=headers)
    ##print(req)
    try:
        response = request.urlopen(req)
        html = response.read().decode("utf-8")
    # 出错的处理
    except urllib.URLError as e:
        ##print('Download error:', e.reason)
        html = None
        # 多次出错的处理
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                #　服务器出错，递归反复尝试
                html = get_html(url, user_agent, num_retries-1)
    return html

# bd doulist-subject
# 通过soup提取到每个电影的全部信息，以list返回
def get_movie_all(html):     
    soup = BeautifulSoup(html,"lxml")
    # 通过元素的属性去找到你想要的元素
    movie_list = soup.find_all('div', class_='bd doulist-subject')
    ##print(movie_list)
    return movie_list

# 提取真正需要的每一部电影数据
def get_movie_one(movie):
    result = []  # 用于存储提取出来的电影信息
    soup_all = BeautifulSoup(str(movie),"lxml")
    title = soup_all.find_all('div', class_='title')
    ##print(title)
    ##print(title[0])
    soup_title = BeautifulSoup(str(title[0]),"lxml")
    ##print(soup_title.stripped_strings)
    # 对获取到的<a>里的内容进行提取
    for line in soup_title.stripped_strings:
        ##print(line)
        result.append(line)

    # num = soup_all.find_all('span', class_='rating_nums')
    num = soup_all.find_all('span')
    result.append(num[1].contents[0])
    

    soup_num = BeautifulSoup(str(num[0]),"lxml")
    for line in soup_num.stripped_strings:  # 对获取到的<span>里的内容进行提取
        result = result + line

    info = soup_all.find_all('div', class_='abstract')
    soup_info = BeautifulSoup(str(info[0]),"lxml")
    result_str = ""
    for line in soup_info.stripped_strings:  # 对获取到的<div>里的内容进行提取
        ##print(line)
        result_str = result_str+ "|| " + line
        ##print(result_str)
    result.append(result_str)
    return result  #返回获取到的结果

def save_file(text, filename):  #保存最终的电影数据
    f= open(filename,'ab')
    f.write(text.encode())
    f.close()

##def CrawlInfo(i):
##    url = 'https://www.douban.com/doulist/3516235/?start='+str(i)+'&sort=seq&sub_type='
##    # 获取当前这个页面的html信息
##    html = get_html(url)
##    # 获取电影的整体信息,这里的list信息正常的长度是25个
##    movie_list = get_movie_all(html)
##    #将每一个div中把每个电影信息提取出来
##    get_movie_one(movie_list[0])
##    for movie in movie_list:
##        result = get_movie_one(movie) # reuslt list
##        #print(result)
##        # 把获取的电影信息格式化，得到需要存储到文件中的信息
##        text = '\t'+'电影名：'+str(result[0])+' | 评分：'+str(result[1])+' | '+str(result[2])+'\n'
##        # 把电影信息存到文件中
##        save_file(text,'豆瓣电影2016.txt')
##        # 每隔1-5秒抓取一页的信息
##        minSecond = 1
##        maxSecond = 5
##        time.sleep(random.randint(minSecond,maxSecond))

def CrawlInfo(url, q):
    # 获取当前这个页面的html信息
    html = get_html(url)
    # 获取电影的整体信息,这里的list信息正常的长度是25个
    movie_list = get_movie_all(html)
    #将每一个div中把每个电影信息提取出来
    get_movie_one(movie_list[0])
    for movie in movie_list:
        result = get_movie_one(movie) # reuslt list
        #print(result)
        # 把获取的电影信息格式化，得到需要存储到文件中的信息
        text = '\t'+'电影名：'+str(result[0])+' | 评分：'+str(result[1])+' | '+str(result[2])+'\n'
        # 把电影信息存到文件中
        save_file(text,'豆瓣电影2016.txt')
        # 每隔1-5秒抓取一页的信息
        minSecond = 1
        maxSecond = 5
        time.sleep(random.randint(minSecond,maxSecond))
    # 完成了当前url的抓取之后，put到队列中去
    q.put(url)
        
if __name__=='__main__':
    # 创建进程池和进程池队列来完成抓取
    pool = Pool()
    q = Manager().Queue()
    
    # 处理入口url信息
    seed_url = "https://www.douban.com/doulist/3516235/?start=200&sort=seq&sub_type="
    CrawlInfo(seed_url,q)
    html = get_html(seed_url)

    # 用正则匹配需要翻页的页面信息
    pattern = re.compile('(https://www.douban.com/doulist/3516235/\?start=.*?)"')
    itemUrls = re.findall(pattern, html)

    # 用队列去模拟广度优先遍历
    crawl_queue = []
    crawled_queue = [] # 抓取过之后的队列信息
    for itemUrl in itemUrls:
        # 通过已经抓取的队列信息来防止重复抓取
        if itemUrl not in crawled_queue: 
            crawl_queue.append(itemUrl)
    # 注意这里的去重操作,这里的set是无序的
    crawl_queue = list(set(crawl_queue))
    ##print(crawl_queue)

    # 抓取队列中的信息为空，则退出循环，说明信息抓取完毕
    while crawl_queue:
        url = crawl_queue.pop()
        # 如果还有需要抓取的url链接信息，这里需要进一步append
        #CrawlInfo(url)
        p.apply_async(func=CrawlInfo, args=(url, q))

        # 当前的url抓取完成，添加到完成队列中去
        url = q.get()
        crawled_queue.append(url)
        
    p.close()
    p.join()
      
##    # 避免magic number
##    startPage = 0
##    endPage = 426
##    step = 25
##    
##    # 用进程池把18个页面以一种兄弟关系来抓取
##    pool = Pool()
##    pool.map(CrawlInfo, [i for i in range(startPage,endPage,step)])
##    pool.close()
##    pool.join()
    
             
