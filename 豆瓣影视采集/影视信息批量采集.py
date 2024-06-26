# 此脚本数据url来源为 url.txt 中
import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor

# 定义请求头，模拟浏览器请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.douban.com/',
    'Connection': 'keep-alive'
}

# 定义处理单个电影信息的函数
def process_movie(url):
    url = url.strip()  # 去除首尾空白字符
    if not url:
        return  # 跳过空行

    # 发送请求获取网页内容
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the web page at {url}. Status code: {response.status_code}")
        return

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取电影标题
    title = soup.find('span', attrs={'property': 'v:itemreviewed'}).text.strip() if soup.find('span', attrs={'property': 'v:itemreviewed'}) else ''

    # 提取评分
    rating_value = soup.find('strong', class_='ll rating_num').text.strip() if soup.find('strong', class_='ll rating_num') else ''

    # 提取评分人数
    rating_count = soup.find('a', class_='rating_people').find('span').text.strip() if soup.find('a', class_='rating_people') and soup.find('a', class_='rating_people').find('span') else ''

    # 提取导演
    director = soup.find('a', rel='v:directedBy').text.strip() if soup.find('a', rel='v:directedBy') else ''

    # 提取主演
    casts = ', '.join([cast.text.strip() for cast in soup.find_all('a', rel='v:starring')]) if soup.find_all('a', rel='v:starring') else ''

    # 提取标签
    genres = ', '.join([genre.text.strip() for genre in soup.find_all('span', property='v:genre')]) if soup.find_all('span', property='v:genre') else ''

    # 提取上映日期
    release_date = soup.find('span', property='v:initialReleaseDate').text.strip() if soup.find('span', property='v:initialReleaseDate') else ''

    # 提取片长和单集片长
    runtime_tag = soup.find('span', property='v:runtime')
    single_runtime_tag = soup.find('span', text='单集片长:')
    
    runtime = ''
    if (runtime_tag):
        runtime = runtime_tag.text.strip()
    elif (single_runtime_tag and single_runtime_tag.next_sibling):
        single_runtime = single_runtime_tag.next_sibling.strip()
        if '分钟' not in single_runtime:
            single_runtime += ' 分钟'
        runtime = single_runtime

    # 提取剧情简介
    summary = soup.find('span', property='v:summary').text.strip() if soup.find('span', property='v:summary') else ''

    # 提取海报图片 URL
    poster_url = soup.find('img', attrs={'rel': 'v:image'})['src'] if soup.find('img', attrs={'rel': 'v:image'}) else ''

    # 提取制片国家/地区
    countries = ''
    countries_tag = soup.find('span', string='制片国家/地区:')
    if countries_tag:
        next_sibling = countries_tag.next_sibling
        countries = next_sibling.strip() if next_sibling and next_sibling.name is None else ''

    # 提取语言
    language = ''
    language_tag = soup.find('span', string='语言:')
    if language_tag:
        next_sibling = language_tag.next_sibling
        language = next_sibling.strip() if next_sibling and next_sibling.name is None else ''

    # 提取又名
    alias = ''
    alias_tag = soup.find('span', string='又名:')
    if alias_tag:
        next_sibling = alias_tag.next_sibling
        alias = next_sibling.strip() if next_sibling and next_sibling.name is None else ''

    # 提取 IMDb 编号
    imdb_value = '无'
    imdb_tag = soup.find('span', string='IMDb:')
    if imdb_tag:
        next_sibling = imdb_tag.next_sibling
        imdb_value = next_sibling.strip() if next_sibling and next_sibling.name is None else None

    # 提取集数
    episodes_value = '1'
    episodes_tag = soup.find('span', string='集数:')
    if episodes_tag:
        next_sibling = episodes_tag.next_sibling
        episodes_value = next_sibling.strip() if next_sibling and next_sibling.name is None else '1'

    # 确定类型：根据集数是否大于1来判断
    if episodes_value.isdigit() and int(episodes_value) > 1:
        movie_type = '电视剧'
    else:
        if '纪录片' in genres:
            movie_type = '纪录片'
        elif '动画' in genres:
            movie_type = '动漫'
        elif '真人秀' in genres:
            movie_type = '综艺'
        else:
            movie_type = '电影'

    return {
        '标题': title,
        '评分': rating_value,
        '评分人数': rating_count,
        '导演': director,
        '主演': casts,
        '标签': genres,
        '类型': movie_type,
        '上映日期': release_date,
        '片长': runtime,
        '剧情简介': summary,
        '海报图片': poster_url,
        '制片国家/地区': countries,
        '语言': language,
        '又名': alias,
        'IMDb': imdb_value,
        '豆瓣url': url,
        '集数': episodes_value
    }

# 打开 CSV 文件准备写入
with open('追剧数据.csv', mode='w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['标题', '评分', '评分人数', '导演', '主演', '标签', '类型', '上映日期', '片长', '剧情简介', '海报图片',
                  '制片国家/地区', '语言', '又名', 'IMDb', '豆瓣url', '集数']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # 从 url.txt 文件中读取 URL 列表
    with open('豆瓣影视采集/url.txt', 'r', encoding='utf-8') as file:
        urls = file.readlines()

    # 使用 ThreadPoolExecutor 来并发处理请求和写入数据 线程数：10
    # 若希望不改变数据顺序，线称数改为1即可
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 提交任务
        futures = [executor.submit(process_movie, url) for url in urls]

        # 处理完成的任务
        for future in futures:
            movie_info = future.result()
            if movie_info:
                writer.writerow(movie_info)
                print(f"电影《{movie_info['标题']}》信息已成功写入到 追剧数据.csv 文件中。")
