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

        # 提取片长和单集片长
        runtime = 'No runtime found'
        runtime_tag = soup.find('span', property='v:runtime')
        single_runtime_tag = soup.find('span', text='单集片长:')
        if runtime_tag:
            runtime = runtime_tag.text.strip()
        elif single_runtime_tag:
            runtime = single_runtime_tag.next_sibling.strip()
            if '分钟' not in runtime:
                runtime += ' 分钟'

        # 提取剧情简介
        summary_tag = soup.find('span', property='v:summary')
        summary = summary_tag.text.strip() if summary_tag else 'No summary found'

        # 提取海报图片 URL
        poster_img_tag = soup.find('img', attrs={'rel': 'v:image'})
        poster_url = poster_img_tag['src'] if poster_img_tag else 'No image found'

        # 提取制片国家/地区
        countries = 'Unknown'
        countries_tag = soup.find('span', string='制片国家/地区:')
        if countries_tag:
            countries_value_tag = countries_tag.find_next('span')  # 可能是下一个兄弟元素
            if countries_value_tag:
                countries = countries_value_tag.text.strip()

        # 提取语言
        language = 'Unknown'
        language_tag = soup.find('span', string='语言:')
        if language_tag:
            language_value_tag = language_tag.find_next('span')  # 可能是下一个兄弟元素
            if language_value_tag:
                language = language_value_tag.text.strip()

        # 提取又名
        alias = 'Unknown'
        alias_tag = soup.find('span', string='又名:')
        if alias_tag:
            alias = alias_tag.next_sibling.strip() if alias_tag.next_sibling else 'Unknown'

        # 提取IMDb编号
        imdb_value = 'Unknown'
        imdb_tag = soup.find('span', string='IMDb:')
        if imdb_tag:
            imdb_value_tag = imdb_tag.find_next_sibling('a')  # IMDb链接通常是一个链接
            imdb_value = imdb_value_tag.text.strip() if imdb_value_tag else 'Unknown'

        # 提取集数
        episodes_value = 'Unknown'
        episodes_tag = soup.find('span', string='集数:')
        if episodes_tag:
            episodes_value = episodes_tag.next_sibling.strip() if episodes_tag.next_sibling else 'Unknown'

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
            '又名': alias,
            'IMDb': imdb_value,
            '豆瓣url': url,
            '集数': episodes_value,
            '单集片长': runtime  # 使用片长字段代替
        })

        print(f"电影《{title}》信息已成功写入到 data.csv 文件中。")
