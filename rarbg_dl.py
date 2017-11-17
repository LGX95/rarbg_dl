#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通过关键字搜索 rarbg.is 发布的资源，并获取第一个搜索结果的磁力链接，
再打开 Mac 上的 Transmission 添加到下载列表中。
如果没有搜索结果，一段时间后再请求搜索，直到添加下载后退出执行。
如果需要验证浏览器，获取新的Cookies再请求
"""

__author__ = 'LGX95'

import logging
import os
import random
import re
import subprocess
import time
import urllib.parse

from datetime import datetime
from io import BytesIO

import requests
import pytesseract

from bs4 import BeautifulSoup
from PIL import Image
from requests import RequestException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from headers import headers

logging.basicConfig(
    level=logging.INFO,
    format = '%(asctime)s %(filename)s : %(levelname)s %(message)s',
    filename = 'rarbg_dl.log',
    filemode = 'w'
    )

SCHEME = 'https'
HOST = 'rarbg.is'
home_path = 'torrents.php'

query = 'the big bang theory'
verify_pattern = re.compile(r'Please wait while we try to verify your browser...')
magnet_pattern = re.compile(r'magnet:.*?')
file = 'test.html'


def get_cookie_string():
    """通过 Selenium 获取新的Cookie，并返回一个Cookie的字符串

    Returns:
        以一个字符串的形式返回Cookie
    """
    url = urllib.parse.urlunparse([SCHEME, HOST, home_path, '', '', ''])
    # 创建一个新的 Selenium WebDriver
    driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
    # driver = webdriver.Firefox()
    # driver = webdriver.Chrome()
    driver.get(url)
    # 创建一个 WebDriverWait 对象
    wait = WebDriverWait(driver, 30)
    try:
        # 等待出现点击跳转的页面
        click_here = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
        # 等待几秒再点击跳转
        time.sleep(random.randint(2, 5))
        click_here.click()
        # 等待填写验证码的表格出现
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'form')))
        # 获得验证码图片的
        img_elem = driver.find_element_by_xpath('//table[@width="100%"]/tbody/tr/td/img')
        img_src = img_elem.get_attribute('src')
        img_rsp = requests.get(img_src)
        im = Image.open(BytesIO(img_rsp.content))
        # im = Image.open(BytesIO(img_elem.screenshot_as_png))
        # 解析验证码
        solve_string = pytesseract.image_to_string(im)
        input = driver.find_element_by_id('solve_string')
        # 填写验证码并回车
        input.send_keys(solve_string)
        input.send_keys(Keys.ENTER)
        # 等待首页出现
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.lista2t')))
        time.sleep(random.randint(5, 10))
        # 获取Cookies
        cookies = driver.get_cookies()
    finally:
        driver.quit()
    cookie_string = ''
    # 将Cookies对象转换为一个字符串
    for item in cookies:
        if item['name'] != '':
            cookie_string += (item['name'] + '=' + item['value'] + '; ')
        else:
            cookie_string += (item['value'] + '; ')
    return cookie_string.strip()


def reset_cookies():
    """重新获取新的 Cookie，将新的 Cookie 写入 headers.py 文件
    """
    cookies = get_cookie_string()
    # 获取文件内容
    with open('headers.py', 'r') as f:
        headers = f.read()
    # 写入新的Cookies
    with open('headers.py', 'w') as f:
        cookies = "'Cookie': '" + cookies + "'"
        f.write(re.sub(r"'Cookie': '.*?'", cookies, headers))



def get_response(url, headers=headers, timeout=30):
    """Get response from url by requests.get

    用get方式得到URL的response对象，对需要验证浏览器的情况抛出异常

    Args:
        url: 请求的URL
        headers: get请求中包含的headers，默认值中包含了User-Agent和Cookie
        timeout: 请求超时时间，默认为30秒

    Returns:
        正常情况下返回一个response对象，获取网页异常时返回None

    Raises:
        在需要验证浏览器的情况下抛出RuntimeError
    """
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == 200:
            # 如果需要验证浏览器，重新获取Cookie并再次请求
            if re.search(verify_pattern, response.text):
                reset_cookies()
                get_response(url)
            return response
        return None
    except RequestException:
        return None


def search(query):
    """search keyword in rarbg.is and return response

    输入的关键字，组建搜索的URL，并get后获取response返回

    Args:
        query: 搜索的关键词，会进行转码

    Returns:
        返回搜索结果的response对象
    """
    query_arg = 'search=' + urllib.parse.quote(query)
    url = urllib.parse.urlunparse([SCHEME, HOST, home_path, '', query_arg, ''])
    return get_response(url)


def get_soup(response):
    """Turn the response to a BeautifulSoup

    将response对象转换为BeautifulSoup返回
    """
    return BeautifulSoup(response.content, 'lxml')


def get_detail_url(soup):
    """get the detail url from the result BeautifulSoup

    处理搜索结果的BeautifulSoup对象，得到第一条结果的链接

    Args:
        soup: 搜索结果的BeautifulSoup对象

    Returns:
        第一条结果的链接
    """

    # 获取包含所有结果的table
    result_table = soup.find(attrs={'class': 'lista2t'})
    # 得到第一个结果
    first_tr = result_table.find('tr', attrs={'class': 'lista2'})
    # 如果没有搜索到结果，返回None
    if first_tr is None:
        return None
    # 得到第一个结果包含跳转链接的a元素
    first_a = first_tr.find('a', href=re.compile(r'/torrent/.*'))
    # 获得跳转链接的path
    detail_path = first_a['href']
    print(first_a.text)
    detail_url = urllib.parse.urlunparse([SCHEME, HOST, detail_path, '', '', ''])
    return detail_url


def get_magnet_link(url):
    """get magnet link from a page

    从一个详情页得到磁力链接

    Args:
        资源详情页的url地址

    Returns:
        磁力链接
    """

    # 如果获取response失败，一直重试
    while True:
        detail_response = get_response(detail_url)
        if detail_response is not None:
            break
    detail_soup = get_soup(detail_response)
    # 通过href属性和正则表达式匹配获取包含磁力链接的a元素
    magnet_a = detail_soup.find('a', href=magnet_pattern)
    # 从href提取磁力链接
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

        # 如果获取response失败，暂停5秒后重试
        if result_response is None:
            # print('Retry...')
            time.sleep(5)
            continue

        result_soup = get_soup(result_response)
        # 将结果网页写入文件，调试时方便使用
        with open(file, 'w') as f:
            f.write(result_soup.prettify())

        detail_url = get_detail_url(result_soup)
        # 如果没得到结果，暂停30分钟后重试
        if detail_url is None:
            log('No result, Waiting for retry...')
            time.sleep(1800)
            continue
        else: # 得到第一个结果，输出详情页链接
            print('detail_url:', detail_url)

        # 获得详情页的磁力链接
        magnet_link = get_magnet_link(detail_url)
        print(magnet_link)

        # 打开Transmission，添加磁力链接到下载列表
        command = 'open -a /Applications/Transmission.app ' + '"' + magnet_link + '"'
        os.system(command)
        break
