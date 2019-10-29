# -*- encoding: utf-8 -*-

from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import request

import re
import json
import os
import datetime as dt


from NaverCaptcha.sites.naver import Naver


class Crawler:
    def __init__(self, dataset_path='./crawled_dataset.json', data_overwriting=False):
        self.main_url = 'https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=cnt&tg=0'
        self.dataset_path = dataset_path
        self.image_path = './images'

        self.int_parser = re.compile('\d+')
        self.link_parser = re.compile('<a href.*</a>')
        self.score_parser = re.compile('\d+\.\d+')

        self.db = {}
        if not data_overwriting and os.path.exists(self.dataset_path):
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                self.db = json.load(f)
                print(f'load exist dataset (len:{len(self.db)})')

        self.wt = 2  # implicitly_wait 인자
        self.driver = None
        self.init_browser()  # 크롬 브라우저 실행


    def init_browser(self):
        self.driver = webdriver.Chrome('chromedriver.exe')
        self.driver.implicitly_wait(self.wt)

    def save_db(self):
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent='\t', ensure_ascii=False)
        print(f'save dataset ({self.dataset_path})')

    @staticmethod
    def daterange(start_page :str, end_page :str):
        start_date = dt.datetime.strptime(start_page, '%Y%m%d').date()
        end_date = dt.datetime.strptime(end_page, '%Y%m%d').date()
        for n in range((end_date - start_date).days + 1):
            yield (start_date + dt.timedelta(n)).strftime('%Y%m%d')

    def start_crawling(self, start_page='20100101', end_page='20100101', crawl_image=False, naver_account=None, print_title=False):
        print('\n-- start crawling --')
        n_data = 0
        if naver_account:
            naver = Naver(self.driver, naver_account['id'], naver_account['pw'])
            naver.clipboard_login(naver.ID, naver.PW)
            print('* login naver *')

        if crawl_image:
            os.makedirs(self.image_path, exist_ok=True)

        for i, date_token in enumerate(self.daterange(start_page, end_page)):
            if i != 0 and i % 10 == 0:  # 10페이지(MV 500개) 마다 저장
                self.save_db()
            print(f'target date: {date_token}')

            target_url = f'{self.main_url}&date={date_token}'
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
                except KeyError:  # 주석 코드가 잡힌 경우
                    continue
                if print_title:
                    print(f'\t - {title}')
                link = tags['href']  # /movie/bi/mi/basic.nhn?code=182699
                code = self.int_parser.findall(link)[0]
                if code in self.db:  # 중복 제외
                    continue
                self.driver.get(f'https://movie.naver.com{tags["href"]}')  # 해당 영화 페이지 접속
                self.driver.implicitly_wait(self.wt)

                try:
                    m_soup = BeautifulSoup(self.driver.page_source)
                except:
                    # 가끔 페이지가 없는 영화가 있음
                    # ex) https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=cnt&tg=0&date=20100722
                    #     22. 걸파이브
                    #     - https://movie.naver.com/movie/bi/mi/basic.nhn?code=76015
                    continue
                summary = m_soup.select('h5.h_tx_story')
                summary = summary[0].text.replace('\xa0', '\n') if summary else ''
                summary = summary.replace(' | ', '\n').replace('|', '')

                contents = m_soup.select('p.con_tx')
                contents = contents[0].text.replace('\xa0', '\n') if contents else ''

                try:
                    _s = m_soup.select('div.main_score > div.score')
                    ems = _s[0].select('div.star_score')[0].select('em')
                    if ems:
                        netizen_score = '0'
                        for x in ems:
                            netizen_score += x.text
                        netizen_score = float(netizen_score)
                    else:
                        netizen_score = -1
                except IndexError:
                    netizen_score = -1

                try:
                    _s = m_soup.select('div.main_score > div.score_left')
                    ems = _s[0].select('div.star_score')[0].select('em')
                    if ems:
                        audience_score = '0'
                        for x in ems:
                            audience_score += x.text
                        audience_score = float(audience_score)
                    else:
                        audience_score = -1
                except IndexError:
                    audience_score = -1

                try:
                    reple = m_soup.select('div.score_reple > p')
                    reple = reple[0].text.replace('\xa0', '\n') if reple else ''
                    reple = reple.lstrip().rstrip()
                except IndexError:
                    reple = ''

                categories = []
                countries = []
                try:
                    spec = m_soup.select('dl.info_spec > dd > p')[0].select('span')
                    for cat in spec[0].select('a'):
                        categories.append(cat.text)
                    for cou in spec[1].select('a'):
                        countries.append(cou.text)
                except IndexError:
                    pass

                try:
                    showtime = int(self.int_parser.findall(spec[2].text)[0])
                except IndexError:
                    showtime = 0

                if crawl_image:
                    try:
                        img_url = m_soup.select('div.poster')[0].select('img')[0]['src']
                        request.urlretrieve(img_url.split('?')[0], os.path.join(self.image_path, f'{code}.jpg'))
                        img_file = f'{code}.jpg'
                    except IndexError:
                        img_file = None

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
                if crawl_image:
                    self.db[code]['image'] = img_file
                #self.driver.back()  # 뒤로가기
                n_data += 1

        n_e_data = len(self.db)
        print('------- end -------\n')
        print(f'current crawled data# : {n_data}')
        print(f'total crawled data# : {n_e_data}')
        print('')

        self.save_db()

        self.driver.close()