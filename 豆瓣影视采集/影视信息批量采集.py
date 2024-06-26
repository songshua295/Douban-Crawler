import requests
from bs4 import BeautifulSoup
import csv
from concurrent.futures import ThreadPoolExecutor
from io import StringIO

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
        return None  # 跳过空行

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查是否请求成功
    except requests.RequestException as e:
        print(f"请求 {url} 失败: {e}")
        return None

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
    runtime = runtime_tag.text.strip() if runtime_tag else single_runtime_tag.next_sibling.strip() + ' 分钟' if single_runtime_tag and single_runtime_tag.next_sibling else ''
    # 提取剧情简介
    summary = soup.find('span', property='v:summary').text.strip() if soup.find('span', property='v:summary') else ''
    # 提取海报图片 URL
    poster_url = soup.find('img', attrs={'rel': 'v:image'})['src'] if soup.find('img', attrs={'rel': 'v:image'}) else ''
    # 提取制片国家/地区
    countries_tag = soup.find('span', string='制片国家/地区:')
    countries = countries_tag.next_sibling.strip() if countries_tag and countries_tag.next_sibling else ''
    # 提取语言
    language_tag = soup.find('span', string='语言:')
    language = language_tag.next_sibling.strip() if language_tag and language_tag.next_sibling else ''
    # 提取又名
    alias_tag = soup.find('span', string='又名:')
    alias = alias_tag.next_sibling.strip() if alias_tag and alias_tag.next_sibling else ''
    # 提取 IMDb 编号
    imdb_tag = soup.find('span', string='IMDb:')
    imdb_value = imdb_tag.next_sibling.strip() if imdb_tag and imdb_tag.next_sibling else '无'
    # 提取集数
    episodes_tag = soup.find('span', string='集数:')
    episodes_value = episodes_tag.next_sibling.strip() if episodes_tag and episodes_tag.next_sibling else '1'
    # 确定类型：根据集数是否大于1来判断
    movie_type = '电视剧' if episodes_value.isdigit() and int(episodes_value) > 1 else '电影'
    if '纪录片' in genres:
        movie_type = '纪录片'
    elif '动画' in genres:
        movie_type = '动漫'
    elif '真人秀' in genres:
        movie_type = '综艺'

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

# 手动输入 URL 列表
urls = []
print("请输入电影的豆瓣 URL（输入 'done' 结束）：")
while True:
    url = input("URL: ").strip()
    if url.lower() == 'done':
        break
    if url:
        urls.append(url)

# 使用 ThreadPoolExecutor 来并发处理请求和处理数据
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_movie, url) for url in urls]

    movie_data = []
    for future in futures:
        movie_info = future.result()
        if movie_info:
            movie_data.append(movie_info)

# 使用 StringIO 来模拟 CSV 文件写入
output = StringIO()
fieldnames = ['标题', '评分', '评分人数', '导演', '主演', '标签', '类型', '上映日期', '片长', '剧情简介', '海报图片',
              '制片国家/地区', '语言', '又名', 'IMDb', '豆瓣url', '集数']
writer = csv.DictWriter(output, fieldnames=fieldnames)
writer.writeheader()
for data in movie_data:
    writer.writerow(data)

# 打印 CSV 内容
print(output.getvalue())
