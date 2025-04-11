import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from time import sleep
import random
import re
import time

# 配置请求头
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "www.baidu.com",
    "Cookie": "BIDUPSID=729E480F1B8CEB5347D8572AE6495CFA; PSTM=1645237046; BAIDUID=729E480F1B8CEB53DEEB6344B7C88A22:FG=1; BD_UPN=123253; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; __yjs_duid=1_695315baa9a328fc73db6db6ba9ee8781645357087938; MSA_WH=1324_311; H_PS_PSSID=35106_31660_35765_34584_35872_35818_35948_35954_35315_26350_22159; H_PS_645EC=ab89Uk1B6EQVOEBnfF64C5jyWp40Rge9HGeQ8Q2fEodX81kjh6WtOKBhR2A; BAIDUID_BFESS=729E480F1B8CEB53DEEB6344B7C88A22:FG=1; BA_HECTOR=2g8g040k818g0l21a31h1g5g60r; baikeVisitId=9a933a90-dc5c-4192-93d2-10526d401267; WWW_ST=1645745708722"
}

# 随机User-Agent列表
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
]

def get_real_url(v_url):
    """
    获取百度链接真实地址
    :param v_url: 百度链接地址
    :return: 真实地址
    """
    try:
        r = requests.get(v_url, headers=headers, allow_redirects=False, timeout=5)
        if r.status_code == 302 or r.status_code == 301:  # 处理重定向
            real_url = r.headers.get('Location')
        else:
            # 尝试从页面内容中提取URL
            try:
                real_url = re.findall("URL='(.*?)'", r.text)[0]
            except (IndexError, AttributeError):
                real_url = v_url  # 如果无法提取，返回原始URL
        
        print('real_url is:', real_url)
        return real_url
    except Exception as e:
        print(f"获取真实URL时出错: {e}")
        return v_url  # 出错时返回原始URL

def main():
    v_keyword = input("请输入搜索关键词：")
    
    # 创建存储数据的列表
    kw_list = []       # 关键词
    page_list = []     # 页码
    title_list = []    # 标题
    href_list = []     # 百度链接
    real_url_list = [] # 真实链接
    desc_list = []     # 简介
    site_list = []     # 网站名称
    
    total_results = 0
    start_time = time.time()
    
    for page in range(6):
        print('开始爬取第{}页'.format(page + 1))
        wait_seconds = random.uniform(1, 2)
        print('开始等待{}秒'.format(wait_seconds))
        sleep(wait_seconds)
        
        # 随机选择User-Agent
        headers["User-Agent"] = random.choice(user_agents)
        
        url = 'https://www.baidu.com/s?wd=' + v_keyword + '&pn=' + str(page * 10)
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            html = r.text
            print('响应码是:{}'.format(r.status_code))
        except requests.exceptions.RequestException as e:
            print(f"请求出错: {e}")
            continue  # 跳过这一页，继续下一页
            
        soup = BeautifulSoup(html, 'html.parser')
        result_list = soup.find_all(attrs={'class':'result c-container xpath-log new-pmd'})
        print('正在爬取:{},共查询到{}个结果'.format(url, len(result_list)))
        total_results += len(result_list)
        
        # 处理每个搜索结果
        for index, result in enumerate(result_list):
            try:
                # 提取标题
                title_element = result.find('h3')
                if title_element:
                    title = title_element.get_text().strip()
                else:
                    title = "无标题"
                
                # 提取百度链接
                a_tag = result.find('h3').find('a') if title_element else None
                if a_tag and 'href' in a_tag.attrs:
                    href = a_tag['href']
                else:
                    href = ""
                
							# 优化网站名称提取 - 尝试多种可能的class
                site_element = result.find(attrs={'class': 'c-showurl'}) or \
                            result.find(attrs={'class': 'c-color-gray'}) or \
                            result.find(attrs={'class': 'c-font-normal'})
                if site_element:
                    site = re.sub(r'\s+', ' ', site_element.get_text().strip())  # 去除多余空格
                    site = re.sub(r'^https?://', '', site)  # 去除开头的http/https
                    site = re.sub(r'/$', '', site)  # 去除结尾的斜杠
                else:
                    site = "未知来源"
                
                # 优化简介提取 - 尝试多种可能的class
                desc_element = result.find(attrs={'class': 'c-abstract'}) or \
                            result.find(attrs={'class': 'content-right_8Zs40'}) or \
                            result.find(attrs={'class': 'c-span-last'})
                if desc_element:
                    desc = re.sub(r'\s+', ' ', desc_element.get_text().strip())
                    # 去除"百度快照"等无关文本
                    desc = re.sub(r'百度快照.*$', '', desc)
                else:
                    # 如果没有简介，尝试从标题后的第一个文本节点获取
                    next_sibling = title_element.find_next_sibling(text=True)
                    desc = next_sibling.strip() if next_sibling else "无简介"
				# # 提取简介
                # desc_element = result.find(attrs={'class': 'c-abstract'})
                # if desc_element:
                #     desc = desc_element.get_text().strip()
                # else:
                #     desc = "无简介"
                
                # # 提取网站名称
                # site_element = result.find(attrs={'class': 'c-showurl'})
                # if site_element:
                #     site = site_element.get_text().strip()
                # else:
                #     site = "未知来源"
                
                # 获取真实链接
                try:
                    real_url = get_real_url(href) if href else ""
                except Exception as e:
                    print(f"获取真实链接失败: {e}")
                    real_url = ""
                
                # 将数据添加到列表
                kw_list.append(v_keyword)
                page_list.append(page + 1)
                title_list.append(title)
                href_list.append(href)
                real_url_list.append(real_url)
                desc_list.append(desc)
                site_list.append(site)
                
                print(f"成功提取第{page+1}页第{index+1}条结果: {title}")
                
            except Exception as e:
                print(f"处理搜索结果时出错: {e}")
                continue
    
    # 创建DataFrame
    df = pd.DataFrame({
        '关键词': kw_list,
        '页码': page_list,
        '标题': title_list,
        '百度链接': href_list,
        '真实链接': real_url_list,
        '简介': desc_list,
        '网站名称': site_list,
    })
    
    # 检查文件是否存在，决定是否写入表头
    if os.path.exists('./shixi.csv'):
        header = None
    else:
        header = ['关键词', '页码', '标题', '百度链接', '真实链接', '简介', '网站名称']
    
    # 保存到CSV
    if not df.empty:
        df.to_csv('./shixi.csv', mode='a+', index=False, header=header, encoding='utf_8_sig')
        print('结果保存成功:{}'.format('./shixi.csv'))
    else:
        print('没有找到任何结果')
    
    end_time = time.time()
    print(f"爬取完成，共获取 {len(title_list)} 条有效结果，耗时 {end_time - start_time:.2f} 秒")

if __name__ == '__main__':
    main()