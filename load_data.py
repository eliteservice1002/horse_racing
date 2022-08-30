
import os
import django
os.environ["DJANGO_SETTINGS_MODULE"] = 'horseracing.settings'
django.setup()
import pandas as pd
import dateutil.parser
from django.utils import timezone

from frontend.models import General, Horse, Player

def db_insert():
    ######## General data inserting #######
    # print('######## General data inserting #######')
    # df_general = pd.read_csv('general_2011.csv')
    # df_general.fillna('', inplace=True)
    # for index, row in df_general.iterrows():
    #     exist = General.objects.filter(link=row["link"]).count()
    #     if exist == 0 :
    #         edate = dateutil.parser.parse(row["edate"])
    #         edate = timezone.make_aware(edate, timezone.get_current_timezone())
    #         handicap_rating_start = 0
    #         handicap_rating_end = 0

    #         if str(row["handicap_rating"]).strip() != "":
    #             (handicap_rating_start, handicap_rating_end)= row["handicap_rating"].split('-')
            
    #         try:
    #             race_class = int(row["race_class"])
    #         except:
    #             race_class = 0

    #         obj = General(
    #             link= row["link"],
    #             sdate= row["date"],
    #             track= row["track"],
    #             country= row["country"],
    #             stime= row["time"],
    #             race_title= row["race_title"],
    #             race_name= row["race_name"],
    #             c1= row["C1"],
    #             c2= row["C2"],
    #             c3= row["C3"],
    #             c4= row["C4"],
    #             c5= row["C5"],
    #             c6= row["C6"],
    #             c7= row["C7"],
    #             c8= row["C8"],
    #             race_class= race_class,
    #             marker= row["marker"],
    #             handicap_rating= row["handicap_rating"],
    #             handicap_rating_start= handicap_rating_start,
    #             handicap_rating_end= handicap_rating_end,
    #             age_class= row["age_class"],
    #             distance_mls= row["distance_mls"],
    #             distance= row["distance"],
    #             going= row["going"],
    #             prize= row["prize"],
    #             total_runners= row["total_runners"],
    #             winning_time= row["winning_time"],
    #             winning_timevar= row["winning_timevar"],
    #             total_sp= row["total_sp"],
    #             edate= edate
    #         )
    #         obj.save()
    # print('####### END #######')

    ######## Horse data inserting ########
    # print('######## Horse data inserting ########')
    # # Horse.objects.all().delete()
    # df_horse = pd.read_csv('horse_2018.csv')
    # df_horse.fillna('', inplace=True)
    # for index, row in df_horse.iterrows():
    #     exist = Horse.objects.filter(link=row["link"]).count()
    #     if exist == 0 :
    #         obj = Horse(
    #             link= row["link"],
    #             birth_date= row["birth_date"],
    #             owner= row["owner"],
    #             owner_history= row["owner_history"]
    #         )
    #         obj.save()
    # print('####### END #######')
    
    # ####### Player data inserting #######
    print('####### Player data inserting #######')
    df_player = pd.read_csv('player_2008_2.csv')
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

def make_draw_index():
    print('####### Make Draw index starting #######')
    objs = General.objects.filter(sdate__gte='2009-01-01', sdate__lte='2009-12-31')
    for obj in objs:
        player_data = Player.objects.filter(racing_id=obj.id).exclude(draw=0).order_by('draw')
        index = 1
        for player_obj in player_data:
            tmp_obj = Player.objects.get(id=player_obj.id)
            tmp_obj.draw_index = index
            tmp_obj.save()
            index = index + 1
    print('####### END #######')
def refactor_db():
    General.objects.filter(sdate__gte='2021-01-01').delete()
    Player.objects.filter(sdate__gte='2021-01-01').delete()

if __name__ == "__main__":
    # db_insert()
    make_draw_index()
    # refactor_db()