#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import urllib.parse
import subprocess
import os
import time
import logging
from datetime import datetime

import requests
from requests import RequestException
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format = '%(asctime)s %(filename)s : %(levelname)s %(message)s',
    filename = 'rarbg_dl.log',
    filemode = 'w'
    )

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
        'Cookie': 'skt=w73n4q3zkt; skt=w73n4q3zkt; q2bquVJn=qCBnZk87; expla2=1%7CSat%2C%2004%20Nov%202017%2017%3A29%3A45%20GMT; LastVisit=1509795476; q2bquVJn=qCBnZk87; tcc; aby=2'
        }

SCHEME = 'https'
HOST = 'rarbg.is'
home_path = 'torrents.php'

query = 'the big bang theory'
verify_pattern = re.compile(r'Please wait while we try to verify your browser...')
magnet_pattern = re.compile(r'magnet:.*?')
file = 'test.html'


def get_response(url, headers=headers, timeout=30):
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            if re.search(verify_pattern, response.text):
                raise RuntimeError('Reset Cookie!')
            return response
        return None
    except RequestException:
        return None


def search(query):
    query_arg = 'search=' + urllib.parse.quote(query)
    url = urllib.parse.urlunparse([SCHEME, HOST, home_path, '', query_arg, ''])
    return get_response(url)


def get_soup(response):
    return BeautifulSoup(response.content, 'lxml')


def get_detail_url(soup):
    result_table = soup.find(attrs={'class': 'lista2t'})
    first_tr = result_table.find('tr', attrs={'class': 'lista2'})
    if first_tr is None:
        return None
    first_a = first_tr.find('a', href=re.compile(r'/torrent/.*'))
    detail_path = first_a['href']
    print(first_a.text)
    detail_url = urllib.parse.urlunparse([SCHEME, HOST, detail_path, '', '', ''])
    return detail_url


def get_magnet_link(url):
    while True:
        detail_response = get_response(detail_url)
        if detail_response is not None:
            break
    detail_soup = get_soup(detail_response)
    magnet_a = detail_soup.find('a', href=magnet_pattern)
    magnet_link = magnet_a['href']
    return magnet_link


def log(string):
    logging.info(string)


if __name__ == '__main__':
    print(datetime.now(), 'Program start...')
    logging.info('Program start...')
    print('Input the keyword: ')
    query = input()
    while True:
        log('Start request...')
        result_response = search(query)

        if result_response is None:
            # print('Retry...')
            time.sleep(5)
            continue

        result_soup = get_soup(result_response)
        with open(file, 'w') as f:
            f.write(result_soup.prettify())

        detail_url = get_detail_url(result_soup)
        if detail_url is None:
            log('No result, Waiting for retry...')
            time.sleep(1800)
            continue
        else:
            print('detail_url:', detail_url)

        magnet_link = get_magnet_link(detail_url)
        print(magnet_link)

        command = 'open -a /Applications/Transmission.app ' + '"' + magnet_link + '"'
        os.system(command)
        break