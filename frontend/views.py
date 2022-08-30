from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.http import HttpResponse
from django.core import serializers

from django.views.decorators.cache import cache_page
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, TemplateView
from django.views.generic import FormView, RedirectView, View
from django.db.models import Q
from django.db.models import Max, Min

from rest_framework.response import Response
from rest_framework.decorators import api_view

import operator
from functools import reduce

from .models import General, Player, Horse
from .serializers import *
import re

import csv
from django.http import StreamingHttpResponse


# Create your views here.
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

def index(request):
    print(request.user)
    if request.user.is_authenticated :
        return redirect("/home/")
    else:
        return render(request, 'login.html')

def ajax_register(request):
    # Register Function
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        email_qs = User.objects.filter(email = email)
        if email_qs.exists():
            return JsonResponse({'err_code': '1', 'description': 'Email is exist, please use another email'})
        password = make_password(password)
        user = User(
            email = email,
            username = username,
            password = password,
            is_active = True,
        )
        user.save()
        return JsonResponse({'err_code': '2', 'description': 'Successfully Registered'})

def ajax_login(request):                                                                                                                         
    if request.method == 'POST':                                                                                                                                                                                                           
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)  

        if User.objects.filter(username=username).count() > 0:
            user = User.objects.get(username=username)
            if user is None:
                return JsonResponse({'err_code': '1', 'description': 'Username is not exist!'})
            if user.check_password(password) is False:
                return JsonResponse({'err_code': '1', 'description': 'password is not correct!'})
            else:                                                                                                  
                if (user is not None and user.status == 1) or user.is_staff:
                    login(request, user)
                    
                    return JsonResponse({'err_code': '2', 'description': 'Successfully logined'})
                elif user is not None and user.status == 0:
                    return JsonResponse({'err_code': '1', 'description': 'You should wait until admin allow you!'})
                elif user is not None and user.status == 2:
                    return JsonResponse({'err_code': '1', 'description': 'Sorry!, You rejected from admin!'})
                return JsonResponse({'err_code': '1', 'description': 'User info is not valid'})
        else:
            return JsonResponse({'err_code': '1', 'description': 'Username is not exist!'})
    
class LogoutView(RedirectView):
    url = '/'
    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

##### admin part #####
@method_decorator([login_required], name='dispatch')
class Users(TemplateView):
    model = User
    template_name = "users.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        
        return context

def ajax_admin_reset_password(request):
    user_id = request.POST.get('user_id')
    password = request.POST.get('password')
    
    user = User.objects.get(id=user_id)
    user.set_password(password)
    user.save()
    return JsonResponse({'err_code': '2'})

def ajax_reset_password(request):
    password = request.POST.get('password')
    old_password = request.POST.get('old_password')
    
    if request.user.check_password(old_password) is False:
        return JsonResponse({'err_code': '1'})
    else:
        request.user.set_password(password)
        request.user.save()
        login(request, request.user)
    
    return JsonResponse({'err_code': '2'})

def ajax_change_status(request):
    user_id = request.POST.get('user_id')
    status = request.POST.get('status')
    user = User.objects.get(id=user_id)
    user.status = status
    user.save()
    return JsonResponse({'err_code': '2'})

def ajax_delete_user(request):
    user_id = request.POST.get('user_id')
    User.objects.get(id=user_id).delete()
    
    return JsonResponse({'err_code': '2'})

@method_decorator([login_required], name='dispatch')
class Scrapping(TemplateView):
    model = ScrapeHistory
    template_name = "scrapping.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = ScrapeHistory.objects.all()
        
        return context
##### General Part #####

@method_decorator([login_required], name='dispatch')
class Racing(TemplateView):
    model = General
    template_name = "racing.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['country'] = General.objects.values('country').order_by('country').distinct()
        context['tracks'] = General.objects.values('track').order_by('track').distinct()
        context['race_classes'] = General.objects.values('race_class').order_by('race_class').distinct()
        context['goings'] = General.objects.values('going').order_by('going').distinct()
        # race_name distinct
        race_names = []
        race_name_tmp_lst = General.objects.values('race_name').order_by('race_name').distinct()
        for item in race_name_tmp_lst:
            for tmp in item["race_name"].split(";"):
                tmp = tmp.strip()
                if tmp in race_names:
                    pass
                else:
                    race_names.append(tmp)
        race_names.sort()
        context['race_names'] = race_names
        
        min_max_qs = General.objects.order_by('sdate')
        context['end_date'] = min_max_qs.last().sdate.strftime('%Y-%m-%d')
        context['start_date'] = min_max_qs.first().sdate.strftime('%Y-%m-%d')
        context['from_date'] = datetime.today().strftime('%Y-%m-%d')
        context['to_date'] = datetime.today().strftime('%Y-%m-%d')
        
        return context

@api_view(['POST'])
def ajax_get_racing(request):
    start_date = request.POST["from_date"]
    end_date = request.POST["to_date"]
    queryset = General.objects.filter(sdate__range=[start_date, end_date] )

    sel_country = request.POST.getlist("sel_country[]")
    if len(sel_country) > 0:
        queryset = queryset.filter(country__in=sel_country)

    sel_track = request.POST.getlist("sel_track[]")
    if len(sel_track) > 0:
        queryset = queryset.filter(track__in=sel_track)

    sel_race_name = request.POST.getlist("sel_race_name[]")
    if len(sel_race_name) > 0:
        queryset = queryset.filter(reduce(operator.or_, (Q(race_name__contains=x) for x in sel_race_name)))
        

    sel_race_class = request.POST.getlist("sel_race_class[]")
    if len(sel_race_class) > 0:
        queryset = queryset.filter(race_class__in=sel_race_class)
    
    sel_going = request.POST.getlist("sel_going[]")
    if len(sel_going) > 0:
        queryset = queryset.filter(going__in=sel_going)

    all_length = queryset.count()
    if all_length > 3000:
        queryset = queryset[:3000]
    serializer = RacingSerializer(queryset, many=True)
    
    return Response({'data': serializer.data, 'all_length': all_length})
    
@method_decorator([login_required], name='dispatch')
class PlayerView(TemplateView):
    model = Player
    template_name = "player.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['horse_countries'] = Player.objects.values('horse_country').order_by('horse_country').distinct()
        min_max_qs = Player.objects.order_by('sdate')
        context['end_date'] = min_max_qs.last().sdate.strftime('%Y-%m-%d')
        context['start_date'] = min_max_qs.first().sdate.strftime('%Y-%m-%d')
        context['from_date'] = datetime.today().strftime('%Y-%m-%d')
        context['to_date'] = datetime.today().strftime('%Y-%m-%d')
        return context

@api_view(['POST'])
def ajax_get_player(request):
    start_date = request.POST["from_date"]
    end_date = request.POST["to_date"]
    queryset = Player.objects.filter(sdate__range=[start_date, end_date] )
    
    horse_countries = request.POST.getlist("horse_country[]")
    if len(horse_countries) > 0:
        queryset = queryset.filter(horse_country__in=horse_countries)
    
    horse_name = request.POST["horse_name"]
    if horse_name is not '':
        queryset = queryset.filter(horse_name__icontains=horse_name)
    
    horse_jockey = request.POST["horse_jockey"]
    if horse_jockey is not '':
        queryset = queryset.filter(horse_jockey__icontains=horse_jockey)

    horse_trainer = request.POST["horse_trainer"]
    if horse_trainer is not '':
        queryset = queryset.filter(horse_trainer__icontains=horse_trainer)

    sire = request.POST["sire"]
    if sire is not '':
        queryset = queryset.filter(sire__icontains=sire)

    dam = request.POST["dam"]
    if dam is not '':
        queryset = queryset.filter(dam__icontains=dam)

    damsire = request.POST["damsire"]
    if damsire is not '':
        queryset = queryset.filter(damsire__icontains=damsire)
    
    all_length = queryset.count()
    if all_length > 2000:
        queryset = queryset[:2000]
    serializer = PlayerSerializer(queryset, many=True)
    return Response({'data': serializer.data, 'all_length': all_length})

@method_decorator([login_required], name='dispatch')
class HorseView(TemplateView):
    model = Horse
    template_name = "horse.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['horses'] = Horse.objects.all()[:200]
        min_max_qs = Horse.objects.order_by('birth_date')
        context['end_date'] = min_max_qs.last().birth_date.strftime('%Y-%m-%d')
        context['start_date'] = min_max_qs.first().birth_date.strftime('%Y-%m-%d')
        context['from_date'] = context['start_date']
        context['to_date'] = context['end_date']
        return context

@api_view(['POST'])
def ajax_get_horse(request):
    start_date = request.POST["from_date"]
    end_date = request.POST["to_date"]
    queryset = Horse.objects.filter(birth_date__range=[start_date, end_date] )

    horse_name = request.POST["horse_name"]
    if horse_name is not '':
        horse_name = horse_name.replace(' ', '-')
        queryset = queryset.filter(link__icontains=horse_name)

    owner_name = request.POST["owner_name"]
    if owner_name is not '':
        queryset = queryset.filter(owner__icontains=owner_name)

    owner_history_name = request.POST["owner_history_name"]
    if owner_history_name is not '':
        queryset = queryset.filter(owner_history__icontains=owner_history_name)
        
    all_length = queryset.count()
    if all_length > 3000:
        queryset = queryset[:3000]
    
    serializer = HorseSerializer(queryset, many=True)
    return Response({'data': serializer.data, 'all_length': all_length})

def sort_age_class(elem):
    try:
        if len(elem["value"]) > 0:
            line = re.sub('[-+]', '', elem["value"])
            if line[0] == "0":
                return 0
            return int(line)
        else: 
            return 0
    except:
        return 0

def sort_position(elem):
    try:
        return int(elem["position"])
    except:
        return 100
    
################ Search Result ############### 
@method_decorator([login_required], name='dispatch')
class Home(TemplateView):
    model = General
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        gen_field_list = []
        for field in General._meta.fields:
            if field.name != "id" and field.name != "edate" and field.name != "handicap_rating_start" and field.name != "handicap_rating_end":
                gen_field_list.append(field.name)
        
        player_field_list = []
        for field in Player._meta.fields:
            if field.name != "id" and field.name != "edate" and field.name != "racing" and field.name != "horse" and field.name != "link" and field.name != "horse_link":
                player_field_list.append(field.name)
        
        
        horse_field_list = []
        for field in Horse._meta.fields:
            if field.name != "id":
                horse_field_list.append(field.name)
        
        context['gen_field_list'] = gen_field_list
        context['player_field_list'] = player_field_list
        context['horse_field_list'] = horse_field_list
        
        context['gen_field_uncheck_list'] = ['stime', 'handicap_rating', 'age_class', 'race_class', 'distance_mls', 'prize', 'winning_time', 'winning_timevar', 'total_sp']
        context['player_field_uncheck_list'] = ['sdate', 'prize_currency', 'prize_money', 'row_index', 'horse_country', 'price_decimal', 'price_fraction', 
            'price_symbol', 'horse_weight', 'dist_upper', 'dist_beaten', 'racecard_number', 'color', 'sex', 'sire_country', 'dam', 'dam_country', 'price_var', 'wind_12']
        context['horse_field_uncheck_list'] = ['birth_date', 'owner_history']

        # General table
        min_max_qs = General.objects.order_by('sdate')
        context['end_date'] = min_max_qs.last().sdate.strftime('%Y-%m-%d')
        context['start_date'] = min_max_qs.first().sdate.strftime('%Y-%m-%d')
        context['from_date'] = datetime.today().strftime('%Y-%m-%d')
        context['to_date'] = datetime.today().strftime('%Y-%m-%d')

        context['country'] = General.objects.values('country').order_by('country').distinct()
        context['tracks'] = General.objects.values('track').order_by('track').distinct()
        context['race_classes'] = General.objects.values('race_class').order_by('race_class').distinct()
        age_classes = General.objects.values('age_class').order_by('age_class').distinct()

        for temp in age_classes:
            temp["value"] = temp["age_class"].replace('yo', '')
        temp1 = list(age_classes)
        temp1.sort(key=sort_age_class)
        context['age_classes'] = temp1
        
        context['goings'] = General.objects.values('going').order_by('going').distinct()
        context['markers'] = General.objects.values('marker').order_by('marker').distinct()
        
        min_max_qs = General.objects.aggregate(
            min_distance=Min('distance'), max_distance=Max('distance'),
            min_total_runners=Min('total_runners'), max_total_runners=Max('total_runners'),
            min_total_sp=Min('total_sp'), max_total_sp=Max('total_sp'),
            max_handicap_rating=Max('handicap_rating_end')
        )
        context["min_distance"] = min_max_qs["min_distance"]
        context["max_distance"] = min_max_qs["max_distance"]
        context["min_total_runners"] = min_max_qs["min_total_runners"]
        context["max_total_runners"] = min_max_qs["max_total_runners"]
        context["min_total_sp"] = min_max_qs["min_total_sp"]
        context["max_total_sp"] = min_max_qs["max_total_sp"]
        context["max_handicap_rating"] = min_max_qs["max_handicap_rating"]


        # race_name distinct
        race_names = []
        race_name_tmp_lst = General.objects.values('race_name').order_by('race_name').distinct()
        for item in race_name_tmp_lst:
            for tmp in item["race_name"].split(";"):
                tmp = tmp.strip()
                if tmp in race_names:
                    pass
                else:
                    race_names.append(tmp)
        race_names.sort()
        context['race_names'] = race_names

        # horse table
        context['horse_countries'] = Player.objects.values('horse_country').order_by('horse_country').distinct()
        positions = Player.objects.values('position').order_by('position').distinct()
        temp1 = list(positions)
        temp1.sort(key=sort_position)
        
        context['positions'] = temp1
        context['birth_years'] = Player.objects.values('birth_year').order_by('birth_year').distinct()
        context['price_symbols'] = Player.objects.values('price_symbol').order_by('price_symbol').distinct()
        context['colors'] = Player.objects.values('color').order_by('color').distinct()
        context['sexs'] = Player.objects.values('sex').order_by('sex').distinct()
        context['sire_countries'] = Player.objects.values('sire_country').order_by('sire_country').distinct()
        context['dam_countries'] = Player.objects.values('dam_country').order_by('dam_country').distinct()
        context['headgears'] = Player.objects.values('headgear').order_by('headgear').distinct()
        # context['wind_12s'] = Player.objects.values('wind_12').order_by('wind_12').distinct()
        
        min_max_qs = Player.objects.aggregate(
            min_draw=Min('draw_index'), max_draw=Max('draw_index'),
            min_horse_age=Min('horse_age'), max_horse_age=Max('horse_age'),
            min_horse_weight=Min('horse_weight'), max_horse_weight=Max('horse_weight'),
            min_racecard_number=Min('racecard_number'), max_racecard_number=Max('racecard_number'),
            min_horse_or=Min('horse_or'), max_horse_or=Max('horse_or'),
            min_horse_ts=Min('horse_ts'), max_horse_ts=Max('horse_ts'),
            min_horse_rpr=Min('horse_rpr'), max_horse_rpr=Max('horse_rpr'),
            min_price_decimal=Min('price_decimal'), max_price_decimal=Max('price_decimal'),
            min_dist_upper=Min('dist_upper'), max_dist_upper=Max('dist_upper'),
            min_dist_beaten=Min('dist_beaten'), max_dist_beaten=Max('dist_beaten'),
        )
        context["min_draw"] = min_max_qs["min_draw"]
        context["max_draw"] = min_max_qs["max_draw"]
        context["min_horse_age"] = min_max_qs["min_horse_age"]
        context["max_horse_age"] = min_max_qs["max_horse_age"]
        context["min_horse_weight"] = min_max_qs["min_horse_weight"]
        context["max_horse_weight"] = min_max_qs["max_horse_weight"]
        context["min_racecard_number"] = min_max_qs["min_racecard_number"]
        context["max_racecard_number"] = min_max_qs["max_racecard_number"]
        context["min_horse_or"] = min_max_qs["min_horse_or"]
        context["max_horse_or"] = min_max_qs["max_horse_or"]
        context["min_horse_ts"] = min_max_qs["min_horse_ts"]
        context["max_horse_ts"] = min_max_qs["max_horse_ts"]
        context["min_horse_rpr"] = min_max_qs["min_horse_rpr"]
        context["max_horse_rpr"] = min_max_qs["max_horse_rpr"]
        context["min_price_decimal"] = min_max_qs["min_price_decimal"]
        context["max_price_decimal"] = min_max_qs["max_price_decimal"]
        context["min_dist_upper"] = min_max_qs["min_dist_upper"]
        context["max_dist_upper"] = min_max_qs["max_dist_upper"]
        context["min_dist_beaten"] = min_max_qs["min_dist_beaten"]
        context["max_dist_beaten"] = min_max_qs["max_dist_beaten"]
        return context

@api_view(['POST'])
def ajax_search_result(request):
    
    if request.POST["b_first"] == "true":
        return Response({'data': [], 'all_length': 0})
    queryset = get_query_set(request)
    
    all_length = queryset.count()
    if all_length > 1000:
        queryset = queryset[:1000]
    serializer = SearchSerializer(queryset, many=True)
    return Response({'data': serializer.data, 'all_length': all_length})

def ajax_get_track_by_country(request):
    sel_country = request.POST.getlist("sel_country[]")
    if len(sel_country) > 0:
        tracks = General.objects.filter(country__in=sel_country).values_list('track', flat=True).order_by('track').distinct()
    else:
        tracks = General.objects.values_list('track', flat=True).order_by('track').distinct()
    print(tracks)
    return JsonResponse({"tracks" : list(tracks)})

class Echo:
    def write(self, value):
        return value

def get_query_set(request):
    start_date = request.POST["from_date"]
    end_date = request.POST["to_date"]
    free_search = request.POST["free_search"]
    print(start_date, end_date, free_search)
    queryset = Player.objects.filter(Q(sdate__range=[start_date, end_date]) & 
        (Q(racing__race_title__icontains=free_search) | Q(racing__race_name__icontains=free_search) | Q(horse_name__icontains=free_search) 
        | Q(racing__track__icontains=free_search) ))
    
    ################# General Filter ##########
    sel_country = request.POST.getlist("sel_country[]")
    print(sel_country)
    if len(sel_country) > 0 and sel_country[0] != '':
        queryset = queryset.filter(racing__country__in=sel_country)

    sel_track = request.POST.getlist("sel_track[]")
    if len(sel_track) > 0 and sel_track[0] != '':
        queryset = queryset.filter(racing__track__in=sel_track)

    sel_race_name = request.POST.getlist("sel_race_name[]")
    if len(sel_race_name) > 0 and sel_race_name[0] != '':
        queryset = queryset.filter(reduce(operator.or_, (Q(racing__race_name__contains=x) for x in sel_race_name)))
    
    sel_race_class = request.POST.getlist("sel_race_class[]")
    if len(sel_race_class) > 0 and sel_race_class[0] != '':
        queryset = queryset.filter(racing__race_class__in=sel_race_class)
    
    sel_age_class = request.POST.getlist("sel_age_class[]")
    if len(sel_age_class) > 0 and sel_age_class[0] != '':
        queryset = queryset.filter(racing__age_class__in=sel_age_class)
    
    sel_going = request.POST.getlist("sel_going[]")
    if len(sel_going) > 0 and sel_going[0] != '':
        queryset = queryset.filter(racing__going__in=sel_going)
    
    sel_marker = request.POST.getlist("sel_marker[]")
    if len(sel_marker) > 0 and sel_marker[0] != '':
        queryset = queryset.filter(racing__marker__in=sel_marker)
    
    # ion slider range
    distance = request.POST["distance"].split(";")
    queryset = queryset.filter(racing__distance__gte=distance[0], racing__distance__lte=distance[1])

    total_sp = request.POST["total_sp"].split(";")
    queryset = queryset.filter(racing__total_sp__gte=total_sp[0], racing__total_sp__lte=total_sp[1])

    total_runners = request.POST["total_runners"].split(";")
    queryset = queryset.filter(racing__total_runners__gte=total_runners[0], racing__total_runners__lte=total_runners[1])
    
    handicap_rating = request.POST["handicap_rating"].split(";")
    queryset = queryset.filter(racing__handicap_rating_start__gte=handicap_rating[0], racing__handicap_rating_end__lte=handicap_rating[1])

    ################ horse filter ###########
    horse_countries = request.POST.getlist("horse_country[]")
    if len(horse_countries) > 0 and horse_countries[0] != '':
        queryset = queryset.filter(horse_country__in=horse_countries)
    
    position = request.POST.getlist("position[]")
    if len(position) > 0 and position[0] != '':
        queryset = queryset.filter(position__in=position)
    
    birth_year = request.POST.getlist("birth_year[]")
    if len(birth_year) > 0 and birth_year[0] != '':
        queryset = queryset.filter(birth_year__in=birth_year)
    
    price_symbol = request.POST.getlist("price_symbol[]")
    if len(price_symbol) > 0 and price_symbol[0] != '':
        queryset = queryset.filter(price_symbol__in=price_symbol)
    
    color = request.POST.getlist("color[]")
    if len(color) > 0 and color[0] != '':
        queryset = queryset.filter(color__in=color)
    
    sex = request.POST.getlist("sex[]")
    if len(sex) > 0 and sex[0] != '':
        queryset = queryset.filter(sex__in=sex)

    horse_name = request.POST["horse_name"]
    if horse_name is not '':
        queryset = queryset.filter(horse_name__icontains=horse_name)
    
    horse_jockey = request.POST["horse_jockey"]
    if horse_jockey is not '':
        queryset = queryset.filter(horse_jockey__icontains=horse_jockey)

    horse_trainer = request.POST["horse_trainer"]
    if horse_trainer is not '':
        queryset = queryset.filter(horse_trainer__icontains=horse_trainer)

    sire = request.POST["sire"]
    if sire is not '':
        queryset = queryset.filter(sire__icontains=sire)
    
    sire_country = request.POST.getlist("sire_country[]")
    if len(sire_country) > 0 and sire_country[0] != '':
        queryset = queryset.filter(sire_country__in=sire_country)

    dam = request.POST["dam"]
    if dam is not '':
        queryset = queryset.filter(dam__icontains=dam)

    dam_country = request.POST.getlist("dam_country[]")
    if len(dam_country) > 0 and dam_country[0] != '':
        queryset = queryset.filter(dam_country__in=dam_country)
    
    damsire = request.POST["damsire"]
    if damsire is not '':
        queryset = queryset.filter(damsire__icontains=damsire)

    headgear = request.POST.getlist("headgear[]")
    if len(headgear) > 0 and headgear[0] != '':
        queryset = queryset.filter(headgear__in=headgear)
    
    # ion slider range
    
    draw = request.POST["draw"].split(";")
    queryset = queryset.filter(draw_index__gte=draw[0], draw_index__lte=draw[1])

    horse_age = request.POST["horse_age"].split(";")
    queryset = queryset.filter(horse_age__gte=horse_age[0], horse_age__lte=horse_age[1])
    
    horse_weight = request.POST["horse_weight"].split(";")
    queryset = queryset.filter(horse_weight__gte=horse_weight[0], horse_weight__lte=horse_weight[1])
    
    racecard_number = request.POST["racecard_number"].split(";")
    queryset = queryset.filter(racecard_number__gte=racecard_number[0], racecard_number__lte=racecard_number[1])
    
    horse_or = request.POST["horse_or"].split(";")
    queryset = queryset.filter(horse_or__gte=horse_or[0], horse_or__lte=horse_or[1])
    
    horse_ts = request.POST["horse_ts"].split(";")
    queryset = queryset.filter(horse_ts__gte=horse_ts[0], horse_ts__lte=horse_ts[1])

    horse_rpr = request.POST["horse_rpr"].split(";")
    queryset = queryset.filter(horse_rpr__gte=horse_rpr[0], horse_rpr__lte=horse_rpr[1])

    price_decimal = request.POST["price_decimal"].split(";")
    queryset = queryset.filter(price_decimal__gte=price_decimal[0], price_decimal__lte=price_decimal[1])

    dist_upper = request.POST["dist_upper"].split(";")
    queryset = queryset.filter(dist_upper__gte=dist_upper[0], dist_upper__lte=dist_upper[1])

    dist_beaten = request.POST["dist_beaten"].split(";")
    queryset = queryset.filter(dist_beaten__gte=dist_beaten[0], dist_beaten__lte=dist_beaten[1])

    return queryset

def export_csv(request):

    selected_fields = request.POST["selected_fields"]
    field_list = selected_fields.split(',')
    
    query_set = get_query_set(request)
    queryset = query_set.values_list(*field_list)
    echo_buffer = Echo()
    csv_writer = csv.writer(echo_buffer)
    rows = []
    column_names = []
    for temp in field_list:
        temp1 = temp.replace("racing__", "")
        temp1 = temp1.replace("horse__", "")
        column_names.append(temp1)
    rows.append(csv_writer.writerow(column_names))
    for row in queryset:
        rows.append(csv_writer.writerow(row))

    response = StreamingHttpResponse(rows, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="users.csv"'
    return response

import pandas as pd
from frontend.scrape.ExtraClasses import Tools
import os
def get_real_field_name(col_name, logic):
    gen_field_list = []
    for field in General._meta.fields:
        if field.name != "id" and field.name != "edate" and field.name != "handicap_rating_start" and field.name != "handicap_rating_end":
            gen_field_list.append(field.name)
    
    player_field_list = []
    for field in Player._meta.fields:
        if field.name != "id" and field.name != "edate" and field.name != "racing" and field.name != "horse" and field.name != "link" and field.name != "horse_link":
            player_field_list.append(field.name)
    
    
    horse_field_list = []
    for field in Horse._meta.fields:
        if field.name != "id":
            horse_field_list.append(field.name)
    
    if col_name in gen_field_list:
        col_name = 'racing__' + col_name
    if col_name in horse_field_list:
        col_name = 'horse__' + col_name
    
    if logic == "in":
        col_name = col_name + "__in"
    if logic == "like":
        col_name = col_name + '__icontains'
    return col_name

def export_csv_query(request):

    csv_file = request.FILES['file']
    
    contents = csv_file.read().decode('UTF-8')
    
    path = "temp.csv"
    f = open(path, 'w', encoding='utf-8')
    f.write(contents)
    f.close()

    nTool = Tools()
    cPath = nTool.cPath()
    df_logic = nTool.read_csv(cPath + '/csv/Logic.csv')
    logic_dict = dict(zip(df_logic['Column'].values.tolist(), df_logic['Logic'].values.tolist()))
    
    df_qry = pd.read_csv(path)    
    df_qry.fillna("", inplace=True)
    col_heads = df_qry.columns.tolist()

    filter_clauses = Q()
    for head in col_heads:
        if head in df_logic['Column'].values.tolist():

            logic = logic_dict.get(head)
            data = df_qry[head].values.tolist()
            search_field_name = get_real_field_name(head, logic)
            
            if logic == 'in':
                filter_clauses &= Q(**{search_field_name: data })

            if logic == '=':
                temp_clauses = []
                for val in data:
                    temp_clauses.append(Q(**{search_field_name: val }))
                filter_clauses &= reduce(operator.or_, temp_clauses)
            if logic == 'like':
                temp_clauses = []
                for val in data:
                    temp_clauses.append(Q(**{search_field_name: val }))
                filter_clauses &= reduce(operator.or_, temp_clauses)
    
    selected_fields = request.POST["selected_fields"]
    field_list = selected_fields.split(',')

    os.remove(path)

    echo_buffer = Echo()
    csv_writer = csv.writer(echo_buffer)
    rows = []
    column_names = []
    for temp in field_list:
        temp1 = temp.replace("racing__", "")
        temp1 = temp1.replace("horse__", "")
        column_names.append(temp1)
    rows.append(csv_writer.writerow(column_names))
    
    if filter_clauses != Q():
        query_set = get_query_set(request).filter(filter_clauses)
        
        queryset = query_set.values_list(*field_list)
        for row in queryset:
            rows.append(csv_writer.writerow(row))

    response = StreamingHttpResponse(rows, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="users.csv"'
    
    return response

from django_q.tasks import async_task
def dango_q_test(request):
    json_payload = {
        "message": "hello world!"
    }
    async_task("frontend.services.sleep_and_print", 10)
    return JsonResponse(json_payload)

def async_load_data(request):
    json_payload = {
        "message": "hello world!"
    }
    async_task("frontend.services.insert_player_data")
    return JsonResponse(json_payload)

def async_load_data_second(request):
    json_payload = {
        "message": "Load data 1, please correct"
    }
    async_task("frontend.services.insert_player_second_data")
    return JsonResponse(json_payload)

def async_refactor_race_name(request):
    json_payload = {
        "message": "Refactor race name started"
    }
    async_task("frontend.services.refactor_race_name")
    return JsonResponse(json_payload)

def manual_scrape(request):
    start_date = request.POST["start_date"]
    end_date = request.POST["end_date"]
    json_payload = {
        "message": "Scrape started"
    }
    async_task("frontend.services.thread_scrape", start_date, end_date, 2, "Manual")
    return JsonResponse(json_payload)

from django_q.models import Schedule
from django.utils import timezone

def schedule_start(request):
    next_run = datetime.utcnow() + timedelta(days=1)
    next_run = next_run.replace(hour=0, minute=30)
    next_run = timezone.make_aware(next_run, timezone.get_current_timezone())
    print(next_run)
    Schedule.objects.all().delete()
    Schedule.objects.create(
        func='frontend.services.schedule_scrape',
        schedule_type=Schedule.DAILY,
        next_run=next_run
    )
    json_payload = {
        "message": "Schedule started"
    }
    return JsonResponse(json_payload)