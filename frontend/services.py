from time import sleep
from .models import General, Horse, Player, ScrapeHistory

import dateutil.parser
from django.utils import timezone

def sleep_and_print(secs):
    sleep(secs)
    print("Task ran!")
    print(General.objects.all().count())
    return True

import time
from datetime import datetime, timedelta
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

from frontend.scrape.GeneralData import gen_res
from frontend.scrape.PlayerData import play_res
from frontend.scrape.HorseData import horse_res
from frontend.scrape.ExtraClasses import Tools

import pandas as pd
def insert_player_data():
    nTool = Tools()
    cPath = nTool.cPath()
    print('####### Player data inserting #######')
    df_player = pd.read_csv(cPath + '/csv/temp.csv')
    df_player.fillna('', inplace=True)
    for index, row in df_player.iterrows():
        exist = Player.objects.filter(link=row["link"], row_index=row["row_index"], sdate=row["date"], horse_name=row["horse_name"]).count()
        if exist == 0 :
            racing_id = General.objects.get(link=row["link"]).pk
            horse_id = Horse.objects.get(link=row["horse_link"]).pk
            obj = Player(
                link= row["link"],
                sdate= row["date"],
                position= row["position"],
                prize_currency= row["prize_currency"],
                prize_money= row["prize_money"],
                row_index= row["row_index"],
                draw= row["draw"],
                horse_name= row["horse_name"],
                horse_country= row["horse_country"],
                price_decimal= row["price_decimal"],
                price_fraction= row["price_fraction"],
                price_symbol= row["price_symbol"],
                horse_age= row["horse_age"],
                birth_year= row["birth_year"],
                horse_weight= row["horse_weight"],
                dist_upper= row["dist_upper"],
                dist_beaten= row["dist_beaten"],
                racecard_number= row["racecard_number"],
                horse_or= row["horse_or"],
                horse_ts= row["horse_ts"],
                horse_rpr= row["horse_rpr"],
                horse_jockey= row["horse_jockey"],
                horse_trainer= row["horse_trainer"],
                color= row["color"],
                sex= row["sex"],
                sire= str(row["sire"]).strip(),
                sire_country= row["sire_country"],
                dam= str(row["dam"]).strip(),
                dam_country= row["dam_country"],
                damsire= str(row["damsire"]).strip(),
                price_var= row["price_var"],
                headgear= row["headgear"],
                wind_12= row["wind_12"],
                horse_link= row["horse_link"],
                racing_id= racing_id,
                horse_id=horse_id
            )
            obj.save()
    print('####### END #######')
    print('####### Make Draw index starting #######')
    objs = General.objects.filter(sdate__gte='2019-10-01', sdate__lte='2019-11-14')
    for obj in objs:
        player_data = Player.objects.filter(racing_id=obj.id).exclude(draw=0).order_by('draw')
        index = 1
        for player_obj in player_data:
            tmp_obj = Player.objects.get(id=player_obj.id)
            tmp_obj.draw_index = index
            tmp_obj.save()
            index = index + 1
    print('####### END #######')

def insert_player_second_data():
    nTool = Tools()
    cPath = nTool.cPath()
    print('####### Player data inserting 11111 #######')
    df_player = pd.read_csv(cPath + '/csv/temp1.csv')
    df_player.fillna('', inplace=True)
    for index, row in df_player.iterrows():
        exist = Player.objects.filter(link=row["link"], row_index=row["row_index"], sdate=row["date"], horse_name=row["horse_name"]).count()
        if exist == 0 :
            racing_id = General.objects.get(link=row["link"]).pk
            horse_id = Horse.objects.get(link=row["horse_link"]).pk
            obj = Player(
                link= row["link"],
                sdate= row["date"],
                position= row["position"],
                prize_currency= row["prize_currency"],
                prize_money= row["prize_money"],
                row_index= row["row_index"],
                draw= row["draw"],
                horse_name= row["horse_name"],
                horse_country= row["horse_country"],
                price_decimal= row["price_decimal"],
                price_fraction= row["price_fraction"],
                price_symbol= row["price_symbol"],
                horse_age= row["horse_age"],
                birth_year= row["birth_year"],
                horse_weight= row["horse_weight"],
                dist_upper= row["dist_upper"],
                dist_beaten= row["dist_beaten"],
                racecard_number= row["racecard_number"],
                horse_or= row["horse_or"],
                horse_ts= row["horse_ts"],
                horse_rpr= row["horse_rpr"],
                horse_jockey= row["horse_jockey"],
                horse_trainer= row["horse_trainer"],
                color= row["color"],
                sex= row["sex"],
                sire= str(row["sire"]).strip(),
                sire_country= row["sire_country"],
                dam= str(row["dam"]).strip(),
                dam_country= row["dam_country"],
                damsire= str(row["damsire"]).strip(),
                price_var= row["price_var"],
                headgear= row["headgear"],
                wind_12= row["wind_12"],
                horse_link= row["horse_link"],
                racing_id= racing_id,
                horse_id=horse_id
            )
            obj.save()
    print('####### END 11111 #######')
    print('####### Make Draw index starting 1111 #######')
    objs = General.objects.filter(sdate__gte='2019-11-15', sdate__lte='2019-12-31')
    for obj in objs:
        player_data = Player.objects.filter(racing_id=obj.id).exclude(draw=0).order_by('draw')
        index = 1
        for player_obj in player_data:
            tmp_obj = Player.objects.get(id=player_obj.id)
            tmp_obj.draw_index = index
            tmp_obj.save()
            index = index + 1
    print('####### END 1111 #######')

def refactor_race_name():
    gen_objs = General.objects.filter(sdate__gte='2019-01-01', sdate__lte='2021-12-31')
    nTool = Tools()
    cPath = nTool.cPath()
    ndf = nTool.read_csv(cPath + '/csv/NamesData.csv')
    print("########## Refactor Race Name Start ###########")
    for obj in gen_objs:
        res = ''
        k = 0
        title = obj.race_title
        df_gen = {
            "C1": "",
            "C2": "",
            "C3": "",
            "C4": "",
            "C5": "",
            "C6": "",
            "C7": "",
            "C8": "",
        }
        
        for i, row in ndf.iterrows():
            if row['Name'] in title:
                res = res + row['C'] + ': ' + row['Name'] + '; '
                df_gen[row['C']] = row['Name']
                k = k + 1

        if k == 0:
            res = 'All Other'
        else:
            res = res[:-1]
        
        try:
            # new categorization rule
            if res == 'All Other': 
                age_class = obj.age_class
                if 'Q.R.' in title:
                    res = 'C2: Conditions; C3: Qualified Riders'
                    df_gen['C2'] = 'Conditions;'
                    df_gen['C3'] = 'Qualified Riders;'
                if 'Pro/Am' in title or 'Pro-Am' in title:
                    res = 'C6: Bumper;'
                    df_gen['C6'] = "Bumper"
                    df_gen['C1'] = ""
                    df_gen['C2'] = ""
                    df_gen['C3'] = ""
                    df_gen['C4'] = ""
                    df_gen['C5'] = ""
                    df_gen['C7'] = ""
                    df_gen['C8'] = ""
                if age_class == '2yo':
                    res = 'C3: Conditions;'
                    df_gen['C1'] = ""
                    df_gen['C2'] = ""
                    df_gen['C3'] = "Conditions"
                    df_gen['C4'] = ""
                    df_gen['C5'] = ""
                    df_gen['C6'] = ""
                    df_gen['C7'] = ""
                    df_gen['C8'] = ""

                if age_class == '3yo':
                    res = 'C4: Rated Race;'
                    df_gen['C1'] = ""
                    df_gen['C2'] = ""
                    df_gen['C3'] = ""
                    df_gen['C4'] = "Rated Race"
                    df_gen['C5'] = ""
                    df_gen['C6'] = ""
                    df_gen['C7'] = ""
                    df_gen['C8'] = ""

                if obj.country == 'Ireland':
                    if 'INH Flat Race' in title:
                        res = 'C6: Bumper;'
                        df_gen['C6'] = "Bumper"
                        df_gen['C4'] = ""
                    else:
                        res = 'C4: Rated Race;'
                        df_gen['C4'] = "Rated Race"
                        df_gen['C6'] = ""
                    
                    df_gen['C1'] = ""
                    df_gen['C2'] = ""
                    df_gen['C3'] = ""
                    df_gen['C5'] = ""
                    df_gen['C7'] = ""
                    df_gen['C8'] = ""
                if obj.country == 'UK' and 'NH Flat Race' in title:
                    res = 'C6: Bumper;'
                    df_gen['C6'] = "Bumper"
                    df_gen['C1'] = ""
                    df_gen['C2'] = ""
                    df_gen['C3'] = ""
                    df_gen['C4'] = ""
                    df_gen['C5'] = ""
                    df_gen['C7'] = ""
                    df_gen['C8'] = ""
                if res == 'All Other' and obj.handicap_rating is not '':
                    res = 'C4: Handicap;'
                    df_gen['C4'] = 'Handicap'
        except Exception as e:
            print(e, ' Parse Error')

        obj.race_name = res
        obj.c1 = df_gen["C1"]
        obj.c2 = df_gen["C2"]
        obj.c3 = df_gen["C3"]
        obj.c4 = df_gen["C4"]
        obj.c5 = df_gen["C5"]
        obj.c6 = df_gen["C6"]
        obj.c7 = df_gen["C7"]
        obj.c8 = df_gen["C8"]
        obj.save()
    print("########## Refactor Race Name End ###########")

def schedule_scrape():
    start_date = (datetime.utcnow() + timedelta(days=-3)).strftime('%Y-%m-%d')
    end_date = datetime.utcnow().strftime('%Y-%m-%d')
    print("schedule scraped", start_date, end_date)
    thread_scrape(start_date, end_date, 1, 'Automatic')

def thread_scrape(start_date, end_date, threads, manual_auto):
    print("Thread started\n")
    nTool = Tools()
    delta = (nTool.toDate(end_date) - nTool.toDate(start_date)).days
    
    if delta < threads:
        threads = delta

    date_pairs = nTool.split_date(start_date, end_date, threads)
    
    # save scrapping history table
    from_to = start_date + ' : ' + end_date
    scrape_obj = ScrapeHistory(
        from_to = from_to,
        type = manual_auto
    )
    scrape_obj.save()
    
    executor = ThreadPoolExecutor(max_workers=threads)
    general_rows = General.objects.count()
    player_rows = Player.objects.count()
    horse_rows = Horse.objects.count()

    for i in range(0, threads):
        d1 = date_pairs[i].split(':')[0]
        d2 = date_pairs[i].split(':')[1]
        print('Thread start: ' + d1 + ' - ' + d2 + '\n')
        executor.submit(main_scrape, d1, d2)
        
    executor.shutdown(wait=True)
    
    print("End Thread\n")
    content = "General table " + str(General.objects.count() - general_rows) + " rows,  \n Player table " + str(Player.objects.count() - player_rows) + " rows, \nHorse table " +  str(Horse.objects.count() - horse_rows) + " rows have been added"
    
    end_at = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
    print(end_at)
    scrape_obj.content = content
    scrape_obj.active = 0
    scrape_obj.end_at = end_at
    scrape_obj.save()

    print("make draw index\n")
    # make draw index after scrapping
    objs = General.objects.filter(sdate__gte=d1, sdate__lt=d2)
    for obj in objs:
        player_data = Player.objects.filter(racing_id=obj.id).exclude(draw=0).order_by('draw')
        index = 1
        for player_obj in player_data:
            tmp_obj = Player.objects.get(id=player_obj.id)
            tmp_obj.draw_index = index
            tmp_obj.save()
            index = index + 1
    

def main_scrape(start_date, end_date):
    nTool = Tools()
    cPath = nTool.cPath()
    
    vdf = nTool.read_csv(cPath + '/csv/VenuesData.csv')
    ndf = nTool.read_csv(cPath + '/csv/NamesData.csv')
    sdf = nTool.read_csv(cPath +'/csv/DistData.csv')
    cndf = nTool.read_csv(cPath +'/csv/CourseNameData.csv')
    ctdf = nTool.read_csv(cPath +'/csv/CourseTitleData.csv')
    cols_general = ['link', 'date', 'track', 'country', 'time', 'race_title', 'race_name', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'race_class',
                    'handicap_rating', 'age_class', 'distance_mls', 'distance', 'going', 'prize', 'total_runners',
                    'winning_time', 'winning_timevar', 'total_sp', 'edate']

    cols_player = ['link', 'date', 'position', 'prize_currency', 'prize_money', 'row_index', 'draw', 'horse_name', 'horse_country', 'price_decimal',
                   'price_fraction', 'price_symbol', 'horse_age', 'birth_year', 'horse_weight', 'dist_upper',
                   'dist_beaten', 'racecard_number', 'horse_or', 'horse_ts', 'horse_rpr', 'horse_jockey',
                   'horse_trainer', 'color', 'sex', 'sire', 'sire_country', 'dam', 'dam_country', 'damsire', 'price_var', 'headgear', 'wind_12', 'horse_link']

    cols_horse = ['link', 'birth_date', 'owner', 'owner_history']

    for single_date in nTool.daterange(nTool.toDate(start_date), nTool.toDate(end_date)):
        next_date = nTool.qtDate(single_date)
        print('Beginning Scrape: ' + next_date + '\n')
        try:
            links_list = page_links(vdf, next_date)


            if len(links_list) == 0:
                print('Already scraped: ' + next_date + '\n')
                continue

            insert_df(links_list, vdf, ndf, sdf, cndf, ctdf, cols_general, cols_player, cols_horse, next_date)
            print('Done Scraping: ' + next_date + '\n')
            

        except Exception as e:
            print(e)
            pass

def insert_df(links_list, vdf, ndf, sdf, cndf, ctdf, cols_gen, cols_play, cols_horse, next_date):
    for link in links_list:
        try:
            all_data = page_results(link, vdf, ndf, sdf, cndf, ctdf, cols_gen, cols_play, cols_horse, next_date)
            insert_general(all_data['general'])
            insert_horse(all_data['horse'])
            insert_player(all_data['player'])
        except Exception as e:
            print(e, ' -- inserting')
            pass

    return


def page_links(vdf, date_f):
    base_url = "https://www.racingpost.com"
    links_url = "/results/" + date_f + "/time-order"

    page = requests.get(base_url + links_url)
    data = page.text
    soup = BeautifulSoup(data, features="html.parser")

    links_list = []
    for link in soup.find_all('a'):
        link_f = link.get('href')
        base_f = "/results/"
        base_f2 = "#fullReplay-resultList"

        if base_f in link_f and \
                date_f in link_f and \
                base_f + date_f not in link_f and \
                base_f2 not in link_f:

            venue = link_f.split('/')[3]

            if venue in vdf[vdf.columns[0]].values:
                links_list.append(base_url + link_f)

    links_list = list(dict.fromkeys(links_list))
    links_list = check_list(links_list, date_f)

    return links_list


def check_list(links_list, date_f):
    
    objs = list(General.objects.filter(sdate=date_f).values_list('link', flat=True))
    objs_player = list(Player.objects.filter(sdate=date_f, horse_rpr=0).order_by('link').values_list('link', flat=True).distinct())

    links_list = [x for x in links_list if x not in objs]
    
    for tmp in objs_player:
        if tmp not in links_list:
            links_list.append(tmp)
    
    return links_list


def loop_data(link):
    n = 0
    while True:
        n = n + 1
        page = requests.get(link)
        data = page.text
        if data != '' or n > 1000:
            break
    return data

def page_results(link, vdf, ndf, sdf, cndf, ctdf, cols_gen, cols_play, cols_horse, next_date):
    data = loop_data(link)
    if data == '':
        return

    soup = BeautifulSoup(data, features="html.parser")
    
    all_data = {}

    df_gen = gen_res(soup, cols_gen, link, next_date, vdf, ndf, cndf, ctdf)
    df_play = play_res(soup, cols_play, link, sdf, next_date)
    df_horse = horse_res(df_play['horse_link'], cols_horse)

    all_data['general'] = df_gen
    all_data['player'] = df_play
    all_data['horse'] = df_horse

    return all_data

def insert_general(df_gen):
    for index, row in df_gen.iterrows():
        exist = General.objects.filter(link=row["link"]).count()
        if exist == 0 :
            edate = dateutil.parser.parse(row["edate"])
            edate = timezone.make_aware(edate, timezone.get_current_timezone())
            handicap_rating_start = 0
            handicap_rating_end = 0

            if row["handicap_rating"] != "":
                (handicap_rating_start, handicap_rating_end)= row["handicap_rating"].split('-')
                try:
                    handicap_rating_start = int(handicap_rating_start)
                except Exception as e:
                    handicap_rating_start = 0
                try:
                    handicap_rating_end = int(handicap_rating_end)
                except Exception as e:
                    handicap_rating_end = 0
            try:
                race_class = int(row["race_class"])
            except:
                race_class = 0
            try:
                obj = General(
                    link= row["link"],
                    sdate= row["date"],
                    track= row["track"],
                    country= row["country"],
                    stime= row["time"],
                    race_title= row["race_title"],
                    race_name= row["race_name"],
                    c1= row["C1"],
                    c2= row["C2"],
                    c3= row["C3"],
                    c4= row["C4"],
                    c5= row["C5"],
                    c6= row["C6"],
                    c7= row["C7"],
                    c8= row["C8"],
                    race_class= race_class,
                    marker= row["marker"],
                    handicap_rating= row["handicap_rating"],
                    handicap_rating_start= handicap_rating_start,
                    handicap_rating_end= handicap_rating_end,
                    age_class= row["age_class"],
                    distance_mls= row["distance_mls"],
                    distance= row["distance"],
                    going= row["going"],
                    prize= row["prize"],
                    total_runners= row["total_runners"],
                    winning_time= row["winning_time"],
                    winning_timevar= row["winning_timevar"],
                    total_sp= row["total_sp"],
                    edate= edate
                )
                obj.save()
            except Exception as e:
                print(e, ' --general inserting', row)
    
def insert_player(df_play):
    ####### Player data inserting #######
    for index, row in df_play.iterrows():
        exist = Player.objects.filter(link=row["link"], row_index=row["row_index"], sdate=row["date"], horse_name=row["horse_name"]).count()
        if exist == 0 :
            racing_id = General.objects.get(link=row["link"]).pk
            horse_id = Horse.objects.get(link=row["horse_link"]).pk
            draw = row["draw"]
            if draw == "":
                draw = 0
            else:
                draw = int(draw)
            try:
                obj = Player(
                    link= row["link"],
                    sdate= row["date"],
                    position= row["position"],
                    prize_currency= row["prize_currency"],
                    prize_money= row["prize_money"],
                    row_index= row["row_index"],
                    draw= draw,
                    horse_name= row["horse_name"],
                    horse_country= row["horse_country"],
                    price_decimal= row["price_decimal"],
                    price_fraction= row["price_fraction"],
                    price_symbol= row["price_symbol"],
                    horse_age= row["horse_age"],
                    birth_year= row["birth_year"],
                    horse_weight= row["horse_weight"],
                    dist_upper= row["dist_upper"],
                    dist_beaten= row["dist_beaten"],
                    racecard_number= row["racecard_number"],
                    horse_or= row["horse_or"],
                    horse_ts= row["horse_ts"],
                    horse_rpr= row["horse_rpr"],
                    horse_jockey= row["horse_jockey"],
                    horse_trainer= row["horse_trainer"],
                    color= row["color"],
                    sex= row["sex"],
                    sire= str(row["sire"]).strip(),
                    sire_country= row["sire_country"],
                    dam= str(row["dam"]).strip(),
                    dam_country= row["dam_country"],
                    damsire= str(row["damsire"]).strip(),
                    price_var= row["price_var"],
                    headgear= row["headgear"],
                    wind_12= row["wind_12"],
                    horse_link= row["horse_link"],
                    racing_id= racing_id,
                    horse_id=horse_id
                )
                obj.save()
            except Exception as e:
                print("player inserting error: ", e, row)
        else:
            try:
                play_obj = Player.objects.get(link=row["link"], row_index=row["row_index"], sdate=row["date"], horse_name=row["horse_name"])
                play_obj.horse_rpr = row["horse_rpr"]
                play_obj.horse_or= row["horse_or"]
                play_obj.horse_ts= row["horse_ts"]
                play_obj.save()
            except Exception as e:
                print("player updating error: ", e, row)

def insert_horse(df_horse):
    ######## Horse data inserting ########
    for index, row in df_horse.iterrows():
        exist = Horse.objects.filter(link=row["link"]).count()
        if exist == 0 :
            try:
                obj = Horse(
                    link= row["link"],
                    birth_date= row["birth_date"],
                    owner= row["owner"],
                    owner_history= row["owner_history"]
                )
                obj.save()
            except Exception as e:
                print(e, " -- horse data new added")
        else:
            obj = Horse.objects.get(link=row["link"])
            obj.owner = row["owner"]
            obj.owner_history = row["owner_history"]
            obj.save()
    