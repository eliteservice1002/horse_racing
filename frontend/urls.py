"""horseracing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from frontend.services import schedule_scrape
from django.urls import path
from django.conf.urls import url
from django.views.decorators.cache import cache_page

from .views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^ajax-signup', ajax_register, name='ajax-signup'),
    url(r'^ajax-signin', ajax_login, name='ajax-signin'),
    url(r'^logout', LogoutView.as_view(), name='logout'),
    url(r'^users', Users.as_view(), name='users'),
    url(r'^ajax-change-status/$', ajax_change_status, name='ajax-change-status'),
	url(r'^ajax-delete-user/$', ajax_delete_user, name='ajax-delete-user'),
	url(r'^ajax-admin-reset-password/$', ajax_admin_reset_password, name='ajax-admin-reset-password'),

    url(r'^scraping', Scrapping.as_view(), name='scraping'),

    # url(r'^home', cache_page(60 * 15)(Home.as_view()), name='home'),
    url(r'^home', Home.as_view(), name='home'),
    url(r'^ajax-export-csv', export_csv, name='ajax-export-csv'),
    url(r'^ajax-search-result', ajax_search_result, name='ajax-search-result'),
    url(r'^ajax-get-track-by-country', ajax_get_track_by_country, name='ajax-get-track-by-country'),
    url(r'^ajax-csv-query', export_csv_query, name='ajax-csv-query'),

    url(r'^racings', Racing.as_view(), name='racings'),
    url(r'^ajax-get-racings', ajax_get_racing, name='ajax-get-racings'),
    
    url(r'^players', PlayerView.as_view(), name='players'),
    url(r'^ajax-get-players', ajax_get_player, name='ajax-get-players'),
    
    url(r'^horse', HorseView.as_view(), name='horse'),
    url(r'^ajax-get-horse', ajax_get_horse, name='ajax-get-horse'),
    
    url(r'^test', dango_q_test, name='test'),
    #url(r'^load_data', async_load_data, name='load_data'),
    #url(r'^second_load_data/', async_load_data_second, name='second_load_data'),
    # url(r'^refactor', async_refactor_race_name, name='refactor'),
    url(r'^ajax-manual-scrape', manual_scrape, name='ajax-manual-scrape'),
    #url(r'^schedule-start', schedule_start, name='schedule-start'),
]
