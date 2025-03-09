import os
import re
import json
import logging

from datetime import datetime as dt
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import dateparser

HEADERS = {
    'Authority': 'www.drikpanchang.com',
    'Accept': ('text/html,application/xhtml+xml,application/xml;'
               'q=0.9,image/webp,image/apng,*/*;'
               'q=0.8,application/signed-exchange;v=b3;q=0.9'),
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36')
}

class HinduCalendar():
    server_url = 'https://www.drikpanchang.com'
    sitemap = {
        'settings': '/settings/drikpanchang-settings.html'
    }
    methods = {
        'assamese': {
            'month': '/assamese/assamese-month-panjika.html',
            'day': '/assamese/assamese-day-panjika.html',
            'lang': 'as',
            'language': 'Assamese (অসমীয়া)'
        },
        'bengali': {
            'month': '/bengali/bengali-month-panjika.html',
            'day': '/bengali/bengali-day-panjika.html',
            'lang': 'bn',
            'language': 'Bengali (বাংলা)',
        },
        'gujarati': {
            'month': '/gujarati/panchang/gujarati-month-panchang.html',
            'day': '/gujarati/panchang/gujarati-day-panchang.html',
            'lang': 'gu',
            'language': 'Gujarati (ગુજરાતી)'
        },
        'hindi': {
            'month': '/panchang/month-panchang.html',
            'day': '/panchang/day-panchang.html',
            'lang': 'hi',
            'language': 'Hindi (हिन्दी)'
        },
        'isckon': {
            'month': '/iskcon/iskcon-month-calendar.html',
            'day': '/iskcon/iskcon-day-calendar.html',
            'lang': 'en',
            'language': 'English'
        },
        'kannada': {
            'month': '/kannada/panchangam/kannada-month-panchangam.html',
            'day': '/kannada/panchangam/kannada-day-panchangam.html',
            'lang': 'kn',
            'language': 'Kannada (ಕನ್ನಡ)',
        },
        'malayalam': {
            'month': '/malayalam/malayalam-month-calendar.html',
            'day': '/malayalam/malayalam-day-calendar.html',
            'lang': 'ml',
            'language': 'Malayalam (മലയാളം)',
            'lang': 'en',
            'language': 'English'
        },
        'marathi': {
            'month': '/marathi/panchang/marathi-month-panchang.html',
            'day': '/marathi/panchang/marathi-day-panchang.html',
            'lang': 'mr',
            'language': 'Marathi (मराठी)',
        },
        'nepali': {
            'month': '/nepali/calendar/nepali-patro.html',
            'day': '/nepali/calendar/nepali-day-patro.html',
            'lang': 'ne',
            'language': 'Nepali (नेपाली)',
        },
        'oriya': {
            'month': '/oriya/oriya-panji.html',
            'day': '/oriya/oriya-day-panji.html',
            'lang': 'or',
            'language': 'Odia (ଓଡ଼ିଆ)',

        },
        'tamil': {
            'month': '/tamil/tamil-month-panchangam.html',
            'day': '/tamil/tamil-day-panchangam.html',
            'lang': 'en',
            'language': 'English',
        },
        'telugu': {
            'month': '/telugu/panchanga/telugu-month-panchanga.html',
            'day': '/telugu/panchanga/telugu-day-panchanga.html',
            'lang': 'en',
            'language': 'English'

        }
    }
    def __init__(self, method='marathi', city='auto',
                 regional_language=False, geonames_id=None,
                 storage_dir=None):
        self._session = requests.Session()
        self.method = None
        self.regional_language = regional_language
        self.city = city
        self.geonames_id = geonames_id
        self.regional_lists = {}
        self.storage_dir = storage_dir
        self.set_method(method)
        self.set_regional_language(regional_language)
        self._session.headers.update(HEADERS)

    def get_languages(self):
        'dpLanguageSettingId'

    def get_date_url(self, date, regional=False, day=False):
        logging.info(
            f"get_date_url(date={date}, regional={regional}, day={day})"
        )
        dmy_split = re.split(r'/|:|\.|-|,', re.sub(r'\s', '', date))
        dd = dmy_split[0].zfill(2)
        mm = dmy_split[1].zfill(2) if len(dmy_split) > 1 else dt.today().month
        yyyy = dmy_split[2] if len(dmy_split) > 2 else dt.today().year
        date = f'{dd}/{mm}/{yyyy}'
        _parse = urlparse(self.method_day_url if day else self.method_url)
        _query = f'lunar-date={date}' if regional else f'date={date}'
        if self.geonames_id:
            _query += f'&geoname-id={self.geonames_id}'

        date_url = _parse._replace(query=_query).geturl()
        return date_url

    def get_details(self, date, regional=False):
        "Work in Progress"
        "TODO: Figure out if this is needed at all"
        logging.info(
            f"get_details(date={date}, regional={regional})"
        )
        date_url = self.get_date_url(date, regional=regional, day=True)
        r = self.get(date_url)
        content = r.content.decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        cell_divs = soup.find_all('div', {'class': 'dpTableCell'})
        key_class = 'dpTableKey'
        val_class = 'dpTableValue'

        details = {}
        for cell in cell_divs:
            if key_class in cell['class']:
                cell_key = cell.get_text()
            if val_class in cell['class']:
                cell_value = cell.get_text()
                details[cell_key] = cell_value
        return soup, details

    def get_date(self, date, regional=False):
        regional_months=[]
        logging.info(
            f"get_date(date={date}, regional={regional})"
        )
        date_url = self.get_date_url(date, regional=regional)
        r = self.get(date_url)
        content = r.content.decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        day_div = soup.find('div', {'class': 'dpDayPanchangWrapper'})
        panchang_div = day_div.find('div', {'class': 'dpPanchang'})
        panchang = {}
        for element in panchang_div.find_all('p', {'class': 'dpElement'}):
            _key = element.find('span', {'class': 'dpElementKey'})
            _key_text = _key.get_text(separator=' ', strip=True)
            _val = element.find('span', {'class': 'dpElementValue'})
            _val_text = _val.get_text(separator=' ', strip=True)
            if _key_text in panchang:
                while _key_text in panchang:
                    _split = _key_text.split(' #')
                    try:
                        _split[1] = str(int(_split[1]) + 1)
                    except IndexError:
                        _split.append('1')
                    _key_text = ' #'.join(_split)
            panchang[_key_text] = _val_text

        scripts = soup.find_all('script')
        for script in scripts:
            script_text = str(script)  # Convert script to text
            if 'dpTimeContext' in script_text:
                regional_str = script_text.split(';')[-4].split('=')[1].strip()
                try:
                    regional_months = json.loads(regional_str)
                    break
                except json.JSONDecodeError:
                    pass
        head_div = soup.find('div', {'class': 'dpPHeaderContent'})
        regional_div = head_div.find('div', {'class': 'dpPHeaderLeftContent'})
        regional_datestring = regional_div.get_text(separator=', ', strip=True)
        regional_split = regional_datestring.split(', ')
        regional_dd = regional_split[0]
        regional_month = regional_split[1].split()[0]
        try:
            regional_mm = str(regional_months.index(regional_month) + 1).zfill(2)
        except:
            regional_month = regional_split[1]
            regional_mm = str(regional_months.index(regional_month) + 1).zfill(2)
        regional_yy = regional_split[4].split()[0]
        regional_date = dateparser.parse(
            f'{regional_dd}/{regional_mm}/{regional_yy}',
            settings={'DATE_ORDER': 'DMY'}
        ).strftime("%d/%m/%Y")
        ce_div = head_div.find('div', {'class': 'dpPHeaderRightContent'})
        ce_date = dateparser.parse(ce_div.get_text(separator=' ', strip=True))
        ce_datestring = ce_date.strftime("%A, %d %B, %Y")
        ce_date = ce_date.strftime("%d/%m/%Y")
        logging.info(f"CE: {ce_date}, Regional: {regional_date}")
        headwrap_div = soup.find('div', {'class': 'dpPHeaderWrapper'})
        event_div = headwrap_div.find('div', {'class': 'dpPHeaderEventList'})
        if event_div:
            event_text = event_div.get_text(separator=' ', strip=True)
        else:
            event_text = None
        date_object = {}
        #date_object['method'] = self.method
        '''date_object['language'] = (
            self.methods[self.method]['language']
            if self.regional_language else
            'English'
        )'''
        #date_object['city'] = self.city
        date_object['ce_date'] = ce_date
        date_object['ce_datestring'] = ce_datestring
        date_object['event'] = event_text
        date_object['regional_date'] = regional_date
        date_object['regional_datestring'] = regional_datestring
        date_object['panchang'] = panchang
        date_object['url'] = date_url
        date_json = json.dumps(date_object, indent=4, ensure_ascii=False)
        decoded_json = json.loads(date_json)
        a=json.dumps(decoded_json, indent=4, ensure_ascii=False)
        print(a)
        return date_object,a

    def get_regional_lists(self):
        r = self.get(self.method_url)
        content = r.content.decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        lists_div = soup.find('div', {'class': 'dpListsWrapper'})
        cards = lists_div.find_all('div', {'class': 'dpCard'})
        regional_lists = {}
        for card in cards:
            header = card.find('h2', {'class': 'dpCardTitle'})
            ol = card.find('ol', {'class': 'dpListContent'})
            if ol and header:
                header_text = header.get_text(separator=' ', strip=True)
                items = ol.find_all('li')
                elements = []
                for item in items:
                    elements.append(item.get_text(separator=' ', strip=True))

                pattern_map = {
                    'Month List': 'month_names',
                    'Nakshatra List': 'nakshatra_names',
                    'Anandadi Yoga Names': 'anandadi_yoga_names',
                    'Yoga Names': 'yoga_names',
                    'Karana Names': 'karana_names',
                    'Tithi Names': 'tithi_names',
                    'Zodiac Names': 'zodiac_names',
                    'Samvatsara Names': 'samvatsara_names'
                }
                for pattern, varname in pattern_map.items():
                    if pattern in header_text:
                        header_text = varname
                        break
                else:
                    logging.warning(f"Unknown Header: {header_text}")

                if header_text in regional_lists:
                    logging.error(f"List '{header_text}' overwritten.")

                regional_lists[header_text] = elements

        self.regional_lists = regional_lists
        if self.storage_dir:
            for known_header in pattern_map.values():
                if known_header in regional_lists:
                    list_filename = f'{self.method}_{known_header}.txt'
                    list_file = os.path.join(self.storage_dir, list_filename)
                    with open(list_file, 'w') as f:
                        f.write('\n'.join(regional_lists[known_header]))
        return regional_lists

    def find_regional_date(self, date):
        return self.get_date(date, regional=True)

    def set_city(self, geonames_id, city):
        logging.info(f"City change: {(self.geonames_id, self.city)} -> "
                     f"{(geonames_id, city)}")
        self.geonames_id = geonames_id
        self.city = city

    def set_regional_language(self, regional):
        if regional:
            language = 'regional'
        else:
            language = 'english'

        self.regional_language = regional
        if language == 'regional':
            lang = self.methods[self.method]['lang']
            numeral = 'regional'
        else:
            lang = 'en'
            numeral = 'english'

        language_cookies = [
                requests.cookies.create_cookie(
                    domain='.drikpanchang.com',
                    name='dkplanguage',
                    value=lang
                ),
                requests.cookies.create_cookie(
                    domain='.drikpanchang.com',
                    name='dkpnumerallocale',
                    value=numeral
                )
            ]
        self.set_cookies(*language_cookies)
        return True

    def set_method(self, method):
        logging.info(f"Method change: '{self.method}' -> '{method}'")
        valid_methods = list(self.methods.keys())
        method = method.strip().lower()
        if method in valid_methods:
            self.method = method
            self.method_url = self.get_url(method)
            self.method_day_url = self.get_url(method, day=True)
            self.set_regional_language(self.regional_language)
        else:
            if method not in self.methods:
                raise RuntimeWarning("Invalid method. "
                                     f"Valid methods are: {valid_methods}")
            return False
        return True

    def set_cookies(self, *cookie_objs):
        for cookie_obj in cookie_objs:
            self._session.cookies.set_cookie(cookie_obj)

    def get_url(self, key, day=False):
        if key in self.sitemap:
            return f'{self.server_url}{self.sitemap[key]}'
        if key in self.methods:
            cal_type = 'day' if day else 'month'
            return f"{self.server_url}{self.methods[key][cal_type]}"

    def get(self, *args, **kwargs):
        return self._session.get(*args, **kwargs)
