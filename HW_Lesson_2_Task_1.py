"""
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы)
с сайта superjob.ru и hh.ru. Приложение должно анализировать несколько страниц сайта(также вводим через
input или аргументы). Получившийся список должен содержать в себе минимум:
    * Наименование вакансии
    * Предлагаемую зарплату (отдельно мин. и отдельно макс. и отдельно валюта)
    * Ссылку на саму вакансию
    * Сайт откуда собрана вакансия
По своему желанию можно добавить еще работодателя и расположение. Данная структура должна быть одинаковая
для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
"""

from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import json
import time
#import re

VACANCY_NAME = 'Data scientist'
# VACANCY_NAME = 'Big Data'

LINK_MAIN_HH = 'https://hh.ru'
LINK_REST_HH = '/search/vacancy'
LINK_REST_HH_THE_VAC = '/vacancy/'

HEADERS_HH = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
                  ' AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/83.0.4103.106 Safari/537.36',
    'Accept': 'text/html, text/plain'
    # ,'Referer': 'https://www.google.ru/'
}

adr_params_hh = {
    'clusters': 'true',
    'search_field': 'name',
    'enable_snippets': 'true',
    'salary': '',
    'st': 'searchVacancy',
    'text': VACANCY_NAME,
    'fromSearch': 'true'
}


def request_hh_for_vac_id(p_page=0):
    time.sleep(0.8)
    # prepare page
    pg_adr_params_hh = adr_params_hh.copy()
    if p_page > 0:
        pg_adr_params_hh['page'] = p_page
    # do request
    response_hh = requests.get(LINK_MAIN_HH + LINK_REST_HH, headers=HEADERS_HH, params=pg_adr_params_hh)
    # info & result
    print(response_hh.url)
    if response_hh.status_code == 200:
        print(f"Success. Status = {response_hh.status_code}")
        return response_hh.text #.encode('utf-8')
    else:
        print(f"Bad result. Status = {response_hh.status_code}")
        return None


def request_hh_for_vac_info(p_vac_id):
    time.sleep(0.8)
    # do request
    response_hh = requests.get(LINK_MAIN_HH + LINK_REST_HH_THE_VAC + p_vac_id, headers=HEADERS_HH)
    # info & result
    print(response_hh.url)
    if response_hh.status_code == 200:
        print(f"Success. Status = {response_hh.status_code}")
        return response_hh.text #.encode('utf-8')
    else:
        print(f"Bad result. Status = {response_hh.status_code}")
        return None


vacancy_id_list = []
cur_page = 0

while True:
    print(f'\nPAGE {cur_page + 1}')
    # request
    res_text = request_hh_for_vac_id(cur_page)
    # game over
    if res_text is None:
        break
    # counting
    soup_hh = bs(res_text, 'lxml')
    cnt = len(soup_hh.find_all('a', {'class': 'bloko-link bloko-link_dimmed HH-VacancyResponsePopup-Link'}))
    print(f"+{cnt} vacancies found")
    # parsing
    all_x_tags = soup_hh.find_all('a', {'class': 'bloko-link bloko-link_dimmed HH-VacancyResponsePopup-Link'})
    for i, i_tag in enumerate(all_x_tags):
        vacancy_id_value = json.loads(i_tag.find('script',
                                                 {'data-name': 'HH/Vacancy/SendResponseAttempt'}
                                                 )['data-params'],
                                      encoding='utf-8'
                                      )['vacancyId']
        # print(i, vacancy_id_value)
        vacancy_id_list.append({'n': len(vacancy_id_list) + 1,
                                'id': vacancy_id_value,
                                'link': LINK_MAIN_HH + LINK_REST_HH_THE_VAC + vacancy_id_value,
                                'site': LINK_MAIN_HH})
    print(len(vacancy_id_list))

    print(f'PAGE {cur_page + 1} done')
    # once more time
    next_tag = soup_hh.find_all('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
    print("next", len(next_tag))
    if len(next_tag) > 0:
        cur_page += 1
    else:
        break

# pprint(vacancy_id_list)


for i_vac in vacancy_id_list:
    # iterating
    res_text = request_hh_for_vac_info(i_vac['id'])
    soup_hh = bs(res_text, 'lxml')
    # parsing
    x_tag = soup_hh.find('div', {'class': 'vacancy-title'})
    i_vac['name'] = x_tag.find('h1', {'class': 'bloko-header-1'}).text
    xx_tag = x_tag.find('p', {'class': 'vacancy-salary'})
    i_vac['salary'] = xx_tag.find('span', {'class': 'bloko-header-2 bloko-header-2_lite'}).text

#pprint(vacancy_id_list)
# save
with open('hh data about vacancy ('+VACANCY_NAME+').json', 'w', encoding='utf-8') as f:
    json.dump(vacancy_id_list, f)