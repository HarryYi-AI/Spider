# 你是最棒的
# All is well
import requests
import re

# 用户代理设置
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'}

# 获取网页源代码
url = 'http://search.cs.com.cn/search?channelid=215308&searchword=新能源汽车'  # 该网址已经简化了一些不必要的参数
res = requests.get(url, headers=headers).text
# print(res)

# 解析网页源代码提取信息
p_title = '<a style="font-size: 16px;color: #0066ff;line-height: 20px" href=".*?" target="_blank">(.*?)</a>'
p_href = '<a style="font-size: 16px;color: #0066ff;line-height: 20px" href="(.*?)" target="_blank">'
p_date = '&nbsp;&nbsp;.*?&nbsp;(.*?)</td>'
title = re.findall(p_title, res)
href = re.findall(p_href, res)
date = re.findall(p_date, res, re.S)  # 因为.*?有匹配换行，所以需要加上re.S忽略换行影响

# 3.清洗并打印数据
source = []  # 创建一个空列表，来添加新闻来源
for i in range(len(title)):
    source.append('中国证券报')
    title[i] = re.sub('<.*?>', '', title[i])  # 清除<xx>格式内容
    date[i] = date[i].strip()  # 清除换行及空格
    date[i] = re.sub('[.]', '-', date[i])  # 将日期中的.号换成-号
    date[i] = date[i].split(' ')[0]  
    print(str(i + 1) + '.' + title[i] + '(' + source[i] + ' ' + date[i] + ')')
    print(href[i])