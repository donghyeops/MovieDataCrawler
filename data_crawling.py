

from selenium import webdriver
from bs4 import BeautifulSoup
import re
import json
import os

main_url = 'https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=pnt&date=20191001'

driver = webdriver.Chrome('C:/Users/sdh/Desktop/study/project/chromedriver.exe')
wt = 3
driver.implicitly_wait(wt)
dataset_path = './crawled_dataset.json'

start_page = 1
end_page = 1
code_parser = re.compile('\d+')
link_parser = re.compile('<a href.*</a>')
score_parser = re.compile('\d+\.\d+')

crawled_dataset = {}
if os.path.exists(dataset_path):
    with open(dataset_path, 'r') as f:
        crawled_dataset = json.load(f)
        print(f'load exist dataset (len:{len(crawled_dataset)})')
n_s_data = len(crawled_dataset)

print('-- start crawling --')
for page in range(start_page, end_page+1):
    print(f'target page: {page}')

    target_url = f'{main_url}&page={page}'
    driver.get(target_url)
    driver.implicitly_wait(wt)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    movie_table = soup.select('table.list_ranking > tbody')  # 현재 페이지의 영화 리스트

    filtered_movies = link_parser.findall(str(movie_table[0]))
    # [['<a href="/movie/bi/mi/basic.nhn?code=87566" title="언터처블: 1%의 우정">언터처블: 1%의 우정</a>',], ...]

    for movie in filtered_movies:
        tags = BeautifulSoup(movie, 'html.parser').select('a')[0]
        try:
            title = tags['title']
        except:  # 주석 코드가 잡힌 경우
            continue
        print(title)
        link = tags['href']  # /movie/bi/mi/basic.nhn?code=182699
        code = code_parser.findall(link)[0]
        if code in crawled_dataset:  # 중복 제외
            continue
        driver.get(f'https://movie.naver.com{tags["href"]}')  # 해당 영화 페이지 접속
        driver.implicitly_wait(wt)

        m_soup = BeautifulSoup(driver.page_source)
        summary = m_soup.select('h5.h_tx_story')
        summary = summary[0].text.replace('\xa0', '\n') if summary else ''

        contents = m_soup.select('p.con_tx')
        contents = contents[0].text.replace('\xa0', '\n') if contents else ''

        netizen_score = '0'
        _s = m_soup.select('div.main_score > div.score')
        ems = _s[0].select('div.star_score')[0].select('em')
        if ems:
            for x in ems:
                netizen_score += x.text
        netizen_score = float(netizen_score)

        audience_score = '0'
        _s = m_soup.select('div.main_score > div.score_left')
        ems = _s[0].select('div.star_score')[0].select('em')
        if ems:
            for x in ems:
                audience_score += x.text
        audience_score = float(audience_score)

        reple = m_soup.select('div.score_reple > p')
        reple = reple[0].text.replace('\xa0', '\n') if reple else ''

        crawled_dataset[code] = {
            'title': title,
            'code': code,
            'netizen_score': netizen_score,
            'audience_score': audience_score,
            'summary': summary,
            'contents': contents,
            'reple': reple
        }
        driver.back()  # 뒤로가기


n_e_data = len(crawled_dataset)
print('-- end --\n\n')
print(f'current crawled data# : {n_e_data-n_s_data}')
print(f'total crawled data# : {n_e_data}')

with open(dataset_path, 'w') as f:
    json.dump(crawled_dataset, f, indent='\t', ensure_ascii=False)

driver.close()