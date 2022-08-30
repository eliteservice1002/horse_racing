
import os
import django
os.environ["DJANGO_SETTINGS_MODULE"] = 'horseracing.settings'
django.setup()
import pandas as pd
import dateutil.parser
from django.utils import timezone

from frontend.models import General, Horse, Player

def make_draw_index():
    objs = General.objects.filter(sdate__gte='2020-11-01', sdate__lte='2020-12-31')
    for obj in objs:
        player_data = Player.objects.filter(racing_id=obj.id).exclude(draw=0).order_by('draw')
        index = 1
        print("------------")
        for player_obj in player_data:
            print(obj.link, obj.total_runners, player_obj.id, player_obj.draw, player_obj.draw_index)
            tmp_obj = Player.objects.get(id=player_obj.id)
            tmp_obj.draw_index = index
            tmp_obj.save()
            index = index + 1

def strip_player():
    objs = Player.objects.filter(sdate__gte='2020-12-01', sdate__lte='2021-06-05')
    for obj in objs:
        obj.sire = str(obj.sire).strip()
        obj.dam = str(obj.dam).strip()
        obj.damsire = str(obj.dam).strip()
        obj.save()
if __name__ == "__main__":
    # make_draw_index()
    strip_player()