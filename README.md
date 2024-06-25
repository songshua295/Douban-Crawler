import requests
from bs4 import BeautifulSoup
import csv

# 定义请求头，模拟浏览器请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.douban.com/',
    'Connection': 'keep-alive'
}

# 打开 CSV 文件准备写入
with open('data.csv', mode='w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['标题', '评分', '评分人数', '导演', '主演', '类型', '上映日期', '片长', '剧情简介', '海报图片',
                  '制片国家/地区', '语言', '又名', 'IMDb', '豆瓣url', '集数', '单集片长']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # 从 url.txt 文件中读取 URL 列表
    with open('url.txt', 'r', encoding='utf-8') as file:
        urls = file.readlines()

    # 遍历每个 URL
    for url in urls:
        url = url.strip()  # 去除首尾空白字符
        if not url:
            continue  # 跳过空行

        # 发送请求获取网页内容
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve the web page at {url}. Status code: {response.status_code}")
            continue

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取电影标题
        title_tag = soup.find('span', attrs={'property': 'v:itemreviewed'})
        title = title_tag.text.strip() if title_tag else 'No title found'

        # 提取评分
        rating_tag = soup.find('strong', class_='ll rating_num')
        rating_value = rating_tag.text.strip() if rating_tag else 'No rating found'

        # 提取评分人数
        rating_count_tag = soup.find('a', class_='rating_people')
        rating_count = rating_count_tag.find('span').text.strip() if rating_count_tag else 'No rating count found'

        # 提取导演
        director_tag = soup.find('a', rel='v:directedBy')
        director = director_tag.text.strip() if director_tag else 'No director found'

        # 提取主演
        casts = [cast.text.strip() for cast in soup.find_all('a', rel='v:starring')] if soup.find_all('a', rel='v:starring') else 'No casts found'

        # 提取类型
        genres = [genre.text.strip() for genre in soup.find_all('span', property='v:genre')] if soup.find_all('span', property='v:genre') else 'No genres found'

        # 提取上映日期
        release_date_tag = soup.find('span', property='v:initialReleaseDate')
        release_date = release_date_tag.text.strip() if release_date_tag else 'No release date found'

        # 提取片长
        runtime_tag = soup.find('span', property='v:runtime')
        runtime = runtime_tag.text.strip() if runtime_tag else 'No runtime found'

        # 提取剧情简介
        summary_tag = soup.find('span', property='v:summary')
        summary = summary_tag.text.strip() if summary_tag else 'No summary found'

        # 提取海报图片 URL
        poster_img_tag = soup.find('img', attrs={'rel': 'v:image'})
        poster_url = poster_img_tag['src'] if poster_img_tag else 'No image found'

        # 提取制片国家/地区
        countries_tag = soup.find('span', string='制片国家/地区:')
        countries = countries_tag.find_next_sibling('span').text.strip() if countries_tag else 'Unknown'

        # 提取语言
        language_tag = soup.find('span', string='语言:')
        language = language_tag.find_next_sibling('span').text.strip() if language_tag else 'Unknown'

        # 提取又名
        alias_tag = soup.find('span', string='又名:')
        alias_value = alias_tag.find_next_sibling('span').text.strip() if alias_tag and alias_tag.find_next_sibling('span') else 'Unknown'

        # 提取IMDb编号
        imdb_tag = soup.find('span', string='IMDb:')
        imdb_value = imdb_tag.find_next_sibling('span').text.strip() if imdb_tag and imdb_tag.find_next_sibling('span') else 'Unknown'

        # 提取集数
        episodes_tag = soup.find('span', string='集数:')
        episodes_value = episodes_tag.find_next_sibling('span').text.strip() if episodes_tag and episodes_tag.find_next_sibling('span') else 'Unknown'

        # 提取单集片长
        single_runtime_tag = soup.find('span', string='单集片长:')
        single_runtime = single_runtime_tag.find_next_sibling('span').text.strip() if single_runtime_tag and single_runtime_tag.find_next_sibling('span') else 'Unknown'

        # 写入 CSV 文件
        writer.writerow({
            '标题': title,
            '评分': rating_value,
            '评分人数': rating_count,
            '导演': director,
            '主演': ', '.join(casts) if isinstance(casts, list) else casts,
            '类型': ', '.join(genres) if isinstance(genres, list) else genres,
            '上映日期': release_date,
            '片长': runtime,
            '剧情简介': summary,
            '海报图片': poster_url,
            '制片国家/地区': countries,
            '语言': language,
            '又名': alias_value,
            'IMDb': imdb_value,
            '豆瓣url': url,
            '集数': episodes_value,
            '单集片长': single_runtime
        })

        print(f"电影《{title}》信息已成功写入到 data.csv 文件中。")
