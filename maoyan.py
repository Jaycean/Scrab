import json
from multiprocessing import Pool
import requests
from requests.exceptions import RequestException
import re

# 把一个网页的html信息取下来
def get_one_page(url):
    try:
        #用get方法发送一次request，得到一个response响应
        response = requests.get(url)
        if response.status_code == 200: # 200表示成功
            return response.text        # 返回html文本信息
        return None
    except RequestException:
        return None

# [\s\S]*?

# <dd>[\s\S]*?board-index.*?>(\d+)</i>[\s\S]*?title=(".*?") class[\s\S]*?data-src="(.*?)"[\s\S]*?<p class="star">
# 匹配提取信息的函数
def parse_one_page(html):
    print("parse one page")
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
                         +'.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         +'.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    #pattern = re.compile('<p class="name">.*?title="([\s\S]*?)".*?data-act=[\s\S]*?<p class="star">([\s\S]*?)</p>[\s\S]*?<p class="releasetime">([\s\S]*?)</p>    </div>')
    items = re.findall(pattern, html)
    for item in items:
        print(item)
        yield {
            'title': item[0],
            'actor': item[1].strip(),
            'time':  item[2]
        }

# 把数据转换成json格式，存储到本地文件
def write_to_file(content):
    with open('猫眼电影.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False)
                + '\n')

# 主体的逻辑
def main(offset):
    print("main")
    # 拼出url链接 
    url = 'http://maoyan.com/board/4?offset=' + str(offset)

    # 下载链接对应的页面 
    html = get_one_page(url)

    # 下载当前页面中的记录数据
    for item in parse_one_page(html): # 解析出来的是真实要存储的数据
        write_to_file(item)


if __name__ == '__main__':
    # 使用进程池去完成任务
    print("Pool")
    pool = Pool()
    pool.map(main, [i*10 for i in range(10)])
    pool.close()  # 通知进程池不会再增加新的任务
    pool.join()   # 等待进程池的任务全部完成
