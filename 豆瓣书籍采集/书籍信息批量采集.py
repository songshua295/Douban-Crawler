import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# 读取 URL 文件
with open('豆瓣书籍采集/url.txt', 'r', encoding='utf-8') as file:
    urls = [line.strip() for line in file if line.strip()]

# 定义爬取函数
def fetch_book_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 定义默认值
        data = {
            '书名': '',
            '封面': '',
            '作者': '',
            '出版社': '',
            '出品方': '',
            '出版年': '',
            '页数': '',
            '定价': '',
            'ISBN': '',
            '豆瓣评分': '',
            '内容简介': '',
            '豆瓣URL': url
        }
        
        # 获取书名
        title_tag = soup.find('span', property='v:itemreviewed')
        if title_tag:
            data['书名'] = title_tag.get_text().strip()
        
        # 获取封面
        cover_tag = soup.find('a', class_='nbg')
        if cover_tag and cover_tag.find('img'):
            data['封面'] = cover_tag.find('img')['src']
        
        # 获取书籍信息
        info_tag = soup.find(id='info')
        if info_tag:
            # 解析 info 中的所有信息
            info_lines = info_tag.get_text(separator='\n').strip().split('\n')
            info_dict = {}
            current_key = None
            for line in info_lines:
                line = line.strip()
                if not line:
                    continue
                if ':' in line:
                    key, value = line.split(':', 1)
                    current_key = key.strip()
                    info_dict[current_key] = value.strip()
                elif current_key:
                    info_dict[current_key] += ' ' + line.strip()
            
            # 获取作者信息
            authors = []
            author_tags = info_tag.find_all('span', class_='pl')
            for tag in author_tags:
                if tag.get_text(strip=True) == '作者':
                    author = tag.find_next_sibling()
                    while author:
                        if author.name == 'a':
                            authors.append(author.get_text(strip=True))
                        elif author.name == 'span' and author.find('a'):
                            authors.extend(a.get_text(strip=True) for a in author.find_all('a'))
                        author = author.find_next_sibling()
                    break
            data['作者'] = ' / '.join(authors)

            # 其他字段获取
            data['出版社'] = info_dict.get('出版社', '')
            data['出品方'] = info_dict.get('出品方', '')
            data['出版年'] = info_dict.get('出版年', '')
            data['页数'] = info_dict.get('页数', '').replace('页', '')
            data['定价'] = info_dict.get('定价', '')
            data['ISBN'] = info_dict.get('ISBN', '')

        # 获取豆瓣评分
        rating_tag = soup.find('strong', property='v:average')
        if rating_tag:
            data['豆瓣评分'] = rating_tag.get_text().strip()
        
        # 获取内容简介
        intro_tag = soup.find('div', class_='intro')
        if intro_tag:
            intro_text = ''.join([p.get_text().strip() for p in intro_tag.find_all('p')])
            data['内容简介'] = intro_text if intro_text else ''
        
        return data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# 使用多线程爬取数据
book_data_list = []

# 用于统计进度
total_books = len(urls)
completed_books = 0

# 使用 ThreadPoolExecutor 并发处理请求
with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_url = {executor.submit(fetch_book_data, url): url for url in urls}

    for future in as_completed(future_to_url):
        url = future_to_url[future]
        try:
            result = future.result()
            if result:
                book_data_list.append(result)
                completed_books += 1
                print(f"书籍《{result['书名']}》信息已成功获取 ：{completed_books}/{total_books}")
        except Exception as e:
            print(f"Error occurred while processing {url}: {e}")

# 将数据保存到CSV文件
output_dir = './'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
output_path = os.path.join(output_dir, '书籍数据.csv')

# 将数据写入 CSV 文件
with open(output_path, 'w', encoding='utf-8-sig', newline='') as csvfile:
    fieldnames = ['书名', '封面', '作者', '出版社', '出品方', '出版年', '页数', '定价', 'ISBN', '豆瓣评分', '内容简介', '豆瓣URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for book_data in book_data_list:
        writer.writerow(book_data)

print(f"数据已保存到 {output_path}")
