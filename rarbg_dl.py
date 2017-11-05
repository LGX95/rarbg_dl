#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import urllib.parse
import subprocess
import os

import requests
from bs4 import BeautifulSoup

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
        'Cookie': 'skt=w73n4q3zkt; skt=w73n4q3zkt; q2bquVJn=qCBnZk87; expla2=1%7CSat%2C%2004%20Nov%202017%2017%3A29%3A45%20GMT; LastVisit=1509795476; q2bquVJn=qCBnZk87; tcc; aby=2'
        }

SCHEME = 'https'
HOST = 'rarbg.is'
home_path = 'torrents.php'
#baseurl = 'https://rarbg.is/torrents.php'

query = 'the big bang theory'
verify_pattern = re.compile('Please wait while we try to verify your browser...')
file = 'test.html'

def get_response(url, headers=headers, timeout=30):
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            return response
        return None
    except RequestException:
        return None

# response = requests.get(baseurl + '?search=' + urllib.parse.quote(query), headers=headers, timeout=30)

def search(query):
    query_arg = 'search=' + urllib.parse.quote(query)
    url = urllib.parse.urlunparse([SCHEME, HOST, home_path, '', query_arg, ''])
    return get_response(url)

# response = get_response(baseurl+'?search='+urllib.parse.quote(query))
result_response = search(query)

if re.search(verify_pattern, result_response.text):
    print('Reset Cookie...')

result_soup = BeautifulSoup(result_response.content, 'lxml')
with open(file, 'w') as f:
    f.write(result_soup.prettify())

result_table = result_soup.find(attrs={'class': 'lista2t'})
first_tr = result_table.find('tr', attrs={'class': 'lista2'})
first_a = first_tr.find('a', href=re.compile(r'/torrent/.*'))
detail_path = first_a['href']
detail_url = urllib.parse.urlunparse([SCHEME, HOST, detail_path, '', '', ''])
print('detail_url:', detail_url)

detail_response = get_response(detail_url)
detail_soup = BeautifulSoup(detail_response.content, 'lxml')
print(detail_soup.title.string)
magnet_a = detail_soup.find('a', href=re.compile(r'magnet:.*?'))
magnet_link = magnet_a['href']
print(magnet_link)

command = 'open -a /Applications/Transmission.app ' + '"' + magnet_link + '"'
print(command)
os.system(command)