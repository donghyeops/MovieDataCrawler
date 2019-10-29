# -*- encoding: utf-8 -*-

from crawler import Crawler
import configparser

import warnings
warnings.filterwarnings("ignore")

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(filenames='config.ini', encoding='utf-8')

    USE_ACCOUNT = config.getboolean('COMMON', 'USE_ACCOUNT')
    CRAWL_IMAGE = config.getboolean('COMMON', 'CRAWL_IMAGE')
    OVERWRITE_DATA = config.getboolean('COMMON', 'OVERWRITE_DATA')
    PRINT_TITLE = config.getboolean('COMMON', 'PRINT_TITLE')
    START_PAGE = config.get('COMMON', 'START_PAGE')
    END_PAGE = config.get('COMMON', 'END_PAGE')

    if USE_ACCOUNT:
        naver_account = {
                'id': config['ACCOUNT']['ID'],
                'pw': config['ACCOUNT']['PASSWORD']
            }
    else:
        naver_account = None

    print(f'start page : {START_PAGE}')
    print(f'end page : {END_PAGE}')
    print(f'login : {USE_ACCOUNT}')
    print(f'data overwriting : {OVERWRITE_DATA}')
    print(f'image crawling : {CRAWL_IMAGE}')

    crawler = Crawler(data_overwriting=OVERWRITE_DATA)
    crawler.start_crawling(start_page=START_PAGE,
                           end_page=END_PAGE,
                           crawl_image=CRAWL_IMAGE,
                           naver_account=naver_account,
                           print_title=PRINT_TITLE)