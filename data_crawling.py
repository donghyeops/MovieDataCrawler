# -*- encoding: utf-8 -*-

from crawler import Crawler
import configparser

if __name__ == '__main__':
    config = configparser.ConfigParser
    config.read('config.cfg')

    USE_ACCOUNT = config.getboolean('COMMON', 'USE_ACCOUNT')

    if USE_ACCOUNT:
        naver_account = {
                'id': config['ACCOUNT']['ID'],
                'pw': config['ACCOUNT']['PASSWORD']
            }
    else:
        naver_account = None

    START_PAGE = config.get('COMMON', 'START_PAGE')
    END_PAGE = config.get('COMMON', 'END_PAGE')

    crawler = Crawler()
    crawler.start_crawling(start_page=START_PAGE, end_page=END_PAGE, naver_account=naver_account)