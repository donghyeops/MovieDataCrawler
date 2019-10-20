# -*- encoding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime as dt

class Crawler:
    def __init__(self, target_day=None, dataset_path='./crawled_dataset.json'):
        if not target_day:
            now = dt.now()
            target_day = f'{now.year}{now.month:02}{now.day - 1:02}'  # 현재 날짜는 아직 안올라온 경우가 있음
        self.main_url = f'https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=pnt&date={target_day}'
        self.dataset_path = dataset_path

        self.int_parser = re.compile('\d+')
        self.link_parser = re.compile('<a href.*</a>')
        self.score_parser = re.compile('\d+\.\d+')

        self.db = {}
        if os.path.exists(self.dataset_path):
            with open(self.dataset_path, 'r') as f:
                self.db = json.load(f)
                print(f'load exist dataset (len:{len(self.db)})')

        self.wt = 2  # implicitly_wait 인자
        self.driver = None
        self.init_browser()  # 크롬 브라우저 실행


    def init_browser(self):
        self.driver = webdriver.Chrome('C:/Users/sdh/Desktop/study/project/chromedriver.exe')
        self.driver.implicitly_wait(self.wt)

    def save_db(self):
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent='\t', ensure_ascii=False)
        print(f'save dataset (n:{len(self.db)}')

    def start_crawling(self, start_page=1, end_page=10, naver_account=None):
        print('-- start crawling --')
        n_data = 0
        if naver_account:
            print('* login naver *')

        for i, page in enumerate(range(start_page, end_page + 1)):
            if i != 0 and i % 10:
                self.save_db()
            print(f'target page: {page}')

            target_url = f'{self.main_url}&page={page}'
            self.driver.get(target_url)
            self.driver.implicitly_wait(self.wt)

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            movie_table = soup.select('table.list_ranking > tbody')  # 현재 페이지의 영화 리스트

            filtered_movies = self.link_parser.findall(str(movie_table[0]))
            # [['<a href="/movie/bi/mi/basic.nhn?code=87566" title="언터처블: 1%의 우정">언터처블: 1%의 우정</a>',], ...]

            for movie in filtered_movies:
                tags = BeautifulSoup(movie, 'html.parser').select('a')[0]
                try:
                    title = tags['title']
                except:  # 주석 코드가 잡힌 경우
                    continue
                print(title)
                link = tags['href']  # /movie/bi/mi/basic.nhn?code=182699
                code = self.int_parser.findall(link)[0]
                if code in self.db:  # 중복 제외
                    continue
                self.driver.get(f'https://movie.naver.com{tags["href"]}')  # 해당 영화 페이지 접속
                self.driver.implicitly_wait(self.wt)

                m_soup = BeautifulSoup(self.driver.page_source)
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

                spec = m_soup.select('dl.info_spec > dd > p')[0].select('span')

                categories = []
                for cat in spec[0].select('a'):
                    categories.append(cat.text)

                countries = []
                for cou in spec[1].select('a'):
                    countries.append(cou.text)

                showtime = int(self.int_parser.findall(spec[2].text)[0])

                self.db[code] = {
                    'title': title,
                    'mv_code': code,
                    'categories': categories,
                    'countries': countries,
                    'showtime(m)': showtime,
                    'summary': summary,
                    'contents': contents,
                    'netizen_score': netizen_score,
                    'audience_score': audience_score,
                    'reple': reple,
                }
                #self.driver.back()  # 뒤로가기
                n_data += 1

        n_e_data = len(self.db)
        print('-- end --\n\n')
        print(f'current crawled data# : {n_data}')
        print(f'total crawled data# : {n_e_data}')

        self.save_db()

        self.driver.close()