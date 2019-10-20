# -*- encoding: utf-8 -*-

from crawler import Crawler

if __name__ == '__main__':
    crawler = Crawler()
    crawler.start_crawling(start_page=1, end_page=100)