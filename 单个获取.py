import requests
from bs4 import BeautifulSoup

# 目标网址
url = 'https://movie.douban.com/subject/35651927/'

# 定义请求头，模拟浏览器请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.douban.com/',
    'Connection': 'keep-alive'
}

# 发送请求获取网页内容
response = requests.get(url, headers=headers)
# 检查请求是否成功
if response.status_code == 200:
    html_content = response.text
else:
    raise Exception(f"Failed to retrieve the web page. Status code: {response.status_code}")

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 提取电影标题
title_tag = soup.find('span', attrs={'property': 'v:itemreviewed'})
title = title_tag.text if title_tag else 'No title found'

# 提取评分
rating_tag = soup.find('strong', class_='ll rating_num')
rating_value = rating_tag.text if rating_tag else 'No rating found'

# 提取评分人数
rating_count_tag = soup.find('a', class_='rating_people')
rating_count = rating_count_tag.find('span').text if rating_count_tag else 'No rating count found'

# 提取导演
director_tag = soup.find('a', rel='v:directedBy')
director = director_tag.text if director_tag else 'No director found'

# 提取主演
casts = [cast.text for cast in soup.find_all('a', rel='v:starring')] if soup.find_all('a', rel='v:starring') else 'No casts found'

# 提取类型
genres = [genre.text for genre in soup.find_all('span', property='v:genre')] if soup.find_all('span', property='v:genre') else 'No genres found'

# 提取上映日期
release_date_tag = soup.find('span', property='v:initialReleaseDate')
release_date = release_date_tag.text if release_date_tag else 'No release date found'

# 提取片长
runtime_tag = soup.find('span', property='v:runtime')
runtime = runtime_tag.text if runtime_tag else 'No runtime found'

# 提取剧情简介
summary_tag = soup.find('span', property='v:summary')
summary = summary_tag.text.strip() if summary_tag else 'No summary found'

# 提取海报图片 URL
poster_div = soup.find('div', id='mainpic')
poster_img = poster_div.find('img') if poster_div else None
poster_url = poster_img['src'] if poster_img else 'No image found'

# 打印提取的信息
print(f"标题: {title}")
print(f"评分: {rating_value}")
print(f"评分人数: {rating_count}")
print(f"导演: {director}")
print(f"主演: {', '.join(casts)}")
print(f"类型: {', '.join(genres)}")
print(f"上映日期: {release_date}")
print(f"片长: {runtime}")
print(f"剧情简介: {summary}")
print(f"海报图片: {poster_url}")
import requests
from bs4 import BeautifulSoup

# 目标网址
url = 'https://movie.douban.com/subject/35651927/'

# 定义请求头，模拟浏览器请求
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.douban.com/',
    'Connection': 'keep-alive'
}

# 发送请求获取网页内容
response = requests.get(url, headers=headers)
# 检查请求是否成功
if response.status_code == 200:
    html_content = response.text
else:
    raise Exception(f"Failed to retrieve the web page. Status code: {response.status_code}")

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 提取电影标题
title_tag = soup.find('span', attrs={'property': 'v:itemreviewed'})
title = title_tag.text if title_tag else 'No title found'

# 提取评分
rating_tag = soup.find('strong', class_='ll rating_num')
rating_value = rating_tag.text if rating_tag else 'No rating found'

# 提取评分人数
rating_count_tag = soup.find('a', class_='rating_people')
rating_count = rating_count_tag.find('span').text if rating_count_tag else 'No rating count found'

# 提取导演
director_tag = soup.find('a', rel='v:directedBy')
director = director_tag.text if director_tag else 'No director found'

# 提取主演
casts = [cast.text for cast in soup.find_all('a', rel='v:starring')] if soup.find_all('a', rel='v:starring') else 'No casts found'

# 提取类型
genres = [genre.text for genre in soup.find_all('span', property='v:genre')] if soup.find_all('span', property='v:genre') else 'No genres found'

# 提取上映日期
release_date_tag = soup.find('span', property='v:initialReleaseDate')
release_date = release_date_tag.text if release_date_tag else 'No release date found'

# 提取片长
runtime_tag = soup.find('span', property='v:runtime')
runtime = runtime_tag.text if runtime_tag else 'No runtime found'

# 提取剧情简介
summary_tag = soup.find('span', property='v:summary')
summary = summary_tag.text.strip() if summary_tag else 'No summary found'

# 提取海报图片 URL
poster_img_tag = soup.find('img', attrs={'rel': 'v:image'})
poster_url = poster_img_tag['src'] if poster_img_tag else 'No image found'

# 打印提取的信息
print(f"标题: {title}")
print(f"评分: {rating_value}")
print(f"评分人数: {rating_count}")
print(f"导演: {director}")
print(f"主演: {', '.join(casts)}")
print(f"类型: {', '.join(genres)}")
print(f"上映日期: {release_date}")
print(f"片长: {runtime}")
print(f"剧情简介: {summary}")
print(f"海报图片: {poster_url}")
