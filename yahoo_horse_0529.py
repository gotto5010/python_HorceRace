# -*- coding: utf-8 -*-

import requests
import pandas as pd
import json, urllib, time, logging, time, re, os
from bs4 import BeautifulSoup
from selenium import webdriver
driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
logging.basicConfig(level=logging.INFO)

csv_path = os.path.abspath(os.path.dirname(__file__)) + '/data/'

# ヤフー競馬の最初のページ
top_page = 'https://keiba.yahoo.co.jp'
first_page = 'https://keiba.yahoo.co.jp/directory/horsesearch/?status=1&p='

# yahoo競馬の最初の１ページめを取得
def get_html(url):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup

logging.info('get HTML of yahoo page')
soup = get_html(first_page)
table = soup.find('table',class_='dataLs mgnBS')
horses = table.findAll('tr')[1:-1]

horse_url_list = []
logging.info('get horse detail URL')
for tr in horses:
    time.sleep(5)
    horse_url = tr.find("a")["href"]
    horse_url_list.append(horse_url)

logging.info('start getting horse attibute')
r = re.compile(r'.*：')
attribute_list = []
blood_list = []

# int = 0
# while int == 3:
for detail_url in horse_url_list:
    time.sleep(5)
    url = top_page + detail_url
    soup_detail = get_html(url)
    horse_table = soup_detail.find('table', {'class':' mgnBS'})
    name = horse_table.find('h1', class_='fntB').text
    attribute_table = horse_table.find('ul', class_='clearFix fntSS')
    attributes = attribute_table.find_all('li')
    temp_list = []
    for attribute in attributes:
        attribute = attribute.text
        attribute = r.sub('', attribute)
        temp_list.append(attribute)
    temp_list.append(name)
    attribute_list.append(temp_list)

    # 血統情報を集める
    dict_parent = {}
    table = soup_detail.find('table', class_='dirTitResult fntSS')
    bloodM = table.findAll('td', class_='bloodM')
    bloodF = table.findAll('td', class_='bloodF')
    bloodM_list = []
    for temp in bloodM:
        temp = temp.text
        bloodM_list.append(temp)
    bloodF_list = []
    for temp in bloodF:
        temp = temp.text
        bloodF_list.append(temp)
    temp_list = [bloodM_list[0], bloodF_list[3], bloodM_list[1], bloodM_list[4], bloodF_list[1], bloodF_list[5]]
    blood_list.append(temp_list)
    logging.info('get horse attribute')
    # int += 1

"""
    dict_parent['parent_M'] = bloodM_list[0]
    dict_parent['parent_F'] = bloodF_list[3]
    dict_parent['parent_MM'] = bloodM_list[1]
    dict_parent['parent_FM'] = bloodM_list[4]
    dict_parent['parent_MF'] = bloodF_list[1]
    dict_parent['parent_FF'] = bloodF_list[5]

"""

df_attribute = pd.DataFrame(attribute_list)
df_blood = pd.DataFrame(blood_list)

print(df_attribute.shape)
print(df_blood.shape)

df = pd.concat([df_attribute, df_blood],axis=1)
df = df.T
df.to_csv(
csv_path + 'horse_data.csv',
sep=",", header=True, mode='a', index=False, encoding='utf-8'
)