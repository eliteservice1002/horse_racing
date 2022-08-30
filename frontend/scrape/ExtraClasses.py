import csv
import re
from datetime import datetime, timedelta
import os
import sys
import numpy as np
import pandas as pd

class Tools(object):

    def cDate(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def tDate(self):
        return datetime.now().strftime('%Y%m%d%H:%M:%S')

    def oDate(self):
        return datetime.now().strftime('%Y-%m-%d')

    def qtDate(self, date_val):
        return date_val.strftime('%Y-%m-%d')

    def toDate(self, date_val):
        return datetime.strptime(date_val, '%Y-%m-%d')

    def toStr(self, date_val):
        return date_val.strftime('%Y-%m-%d')

    def strDate(self, date_val):
        return datetime.strptime(date_val, '%d %b %Y')

    def dateDiff(self, start_date, end_date):
        s_date = self.toDate(start_date)
        e_date = self.toDate(end_date)

        diff = (e_date - s_date)

        return diff.days

    def nextDay(self, date_val):
        return date_val + timedelta(days=1)

    def trunc_date(self, date_val):
        return datetime.date(date_val)

    def rem_nums(self, text):
        return re.sub(r'\d+', '', text)

    def is_int(self, s):
        try: 
            int(s)
            return True
        except ValueError:
            return False
    
    def trim_str(self, text):
        return re.sub("\n\s*\n*", "\n", text).rstrip().lstrip()

    def rem_br(self, text):
        return text.replace('(', '').replace(')', '')

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def remove_quotes(self, input):
        input = input.replace("'", "") \
            .replace('"', '') \
            .replace('/*', '') \
            .replace('-- ', '') \
            .replace('#', '') \
            .replace('%', '')

        return input

    def to_csv(self, file_name, data_list):
        with open(file_name, 'w', encoding='utf-8-sig', newline='') as f:
            wr = csv.writer(f)
            for rows in data_list:
                wr.writerow([rows])

    def a_csv(self, file_name, data_list):
        with open(file_name, 'a', encoding='utf-8-sig', newline='') as f:
            wr = csv.writer(f)
            wr.writerow(data_list)

    def read_csv(self, name):
        df = pd.read_csv(name, encoding='utf-8-sig')
        return df

    def split_date(self, start_date, end_date, chunks):
        s_date = self.toDate(start_date)
        e_date = self.toDate(end_date)

        diff = (e_date - s_date) / chunks

        date_list = []
        for i in range(0, chunks + 1):
            date_val = s_date + diff * i
            date_list.append(self.trunc_date(date_val))

        date_pairs = []
        for i in range(0, len(date_list) - 1):
            date_pairs.append(str(date_list[i]) + ':' + str(date_list[i + 1]))

        return date_pairs

    def format_time(self, time_val):

        split_time = time_val.split('m')
        min = float(0)
        sec = float(0)

        if len(split_time) == 1:
            if 'm' in time_val:
                min = float(time_val.replace('m', '')) * 60
            if 's' in time_val:
                sec = float(time_val.replace('s', ''))

        if len(split_time) == 2:
            min = float(split_time[0]) * 60
            sec = float(split_time[1].replace('s', '').lstrip())

        res = min + sec

        return res

    def dist_conv(self, value):
        value_split = value.replace('m', 'm,').replace('f', 'f,').split(',')

        res = float(0)
        for val in value_split:
            if 'm' in val:
                res = res + float(val.replace('m', ''))
            if 'f' in val:
                res = res + float(val.replace('f', '')) / 8
            if 'yds' in val:
                res = res + float(val.replace('yds', '')) / 1760

        return float(round(res, 4))

    def num_let(self, value):
        res = re.findall('\d+|\D+', value)
        return res

    def scrape_one(self, soup, class_name):
        res = ''
        try:
            res = soup.select_one(class_name).text
        except:
            pass
        return res

    def scrape_all(self, soup, class_name):
        data = []
        try:
            for child in soup.select(class_name):
                data.append(self.trim_str(str(child.text)))
        except:
            pass
        return data

    def scrape_all_links(self, soup, class_name):
        base_url = "https://www.racingpost.com"
        data = []
        for link in soup.find_all('a', {'class': class_name}):
            try:
                data.append(base_url + link['href'])
            except:
                pass
        return data

    def list_zero(self, data):
        if len(data) == 0:
            return ''
        return data

    def replace_abbr(self, value, sdf):
        try:
            res = float(value)
        except:
            res = float(round(sdf['Dist'][sdf[sdf.Abbr.str.match('nk')].index[0]], 4))

        return res

    def replace_odds(self, value):
        value = value.replace('½', '.5') \
            .replace('¾', '.75') \
            .replace('¼', '.25')
        if value[:1] == '.':
            value = '0' + value

        return value

    def check_dates(self, start_date, end_date):
        if "Date" in start_date:
            return True

        if "Date" in end_date:
            return True

        if self.dateDiff(start_date, end_date) < 1:
            return True

        return False

    def cPath(self):
        
        return str(os.path.abspath(os.path.dirname(__file__)))

    def double_quote(self, val):
        return val.replace("'", "''")

    def split_combine(self, txt):
        txt_split = txt.split('(')

        if '(' in txt:
            res = txt_split[0].rstrip() + ' (' + txt_split[1].lstrip()
        else:
            res = txt_split[0].rstrip()

        return res
