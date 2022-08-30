from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    status = models.IntegerField(null=True, blank=True, default=0)
    def __str__(self):
        return self.username

class ScrapeHistory(models.Model):
    from_to = models.CharField(max_length=32, blank=True, null=True)
    content = models.TextField(max_length=256, blank=True, null=True)
    active = models.IntegerField(null=True, blank=True, default=1)
    type = models.CharField(max_length=24, blank=True, null=True, default='Automatic')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    class Meta:
        db_table = 'ho_scrape_history'
        ordering = ['-created_at']

class General(models.Model):
    link = models.CharField(max_length=200)
    sdate = models.DateField(blank=True, null=True)
    track = models.CharField(max_length=32, blank=True, null=True)
    country = models.CharField(max_length=32, blank=True, null=True)
    stime = models.TimeField(blank=True, null=True)
    race_title = models.CharField(max_length=200, blank=True, null=True)
    race_name = models.CharField(max_length=100, blank=True, null=True)
    c1 = models.CharField(max_length=30, blank=True, null=True)
    c2 = models.CharField(max_length=30, blank=True, null=True)
    c3 = models.CharField(max_length=30, blank=True, null=True)
    c4 = models.CharField(max_length=30, blank=True, null=True)
    c5 = models.CharField(max_length=30, blank=True, null=True)
    c6 = models.CharField(max_length=30, blank=True, null=True)
    c7 = models.CharField(max_length=30, blank=True, null=True)
    c8 = models.CharField(max_length=30, blank=True, null=True)
    race_class = models.IntegerField(blank=True, null=True)
    marker = models.CharField(max_length=15, blank=True, null=True)
    handicap_rating = models.CharField(max_length=15, blank=True, null=True)
    handicap_rating_start = models.IntegerField(blank=True, null=True, default=0)
    handicap_rating_end = models.IntegerField(blank=True, null=True, default=0)
    age_class = models.CharField(max_length=15, blank=True, null=True)
    distance_mls = models.FloatField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    going = models.CharField(max_length=25, blank=True, null=True)
    prize = models.CharField(max_length=250, blank=True, null=True)
    total_runners = models.IntegerField(blank=True, null=True)
    winning_time = models.FloatField(blank=True, null=True)
    winning_timevar = models.FloatField(blank=True, null=True)
    total_sp = models.IntegerField(blank=True, null=True)
    edate = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.link
    
    def prize_as_list(self):
        return self.prize.split(';')
    def race_name_as_list(self):
        return self.race_name.split(';')
    class Meta:
        db_table = 'ho_racing'

class Player(models.Model):
    link = models.CharField(max_length=200)
    sdate = models.DateField(blank=True, null=True)
    position = models.CharField(max_length=5, blank=True, null=True)
    prize_currency = models.CharField(max_length=32, blank=True, null=True)
    prize_money = models.FloatField(blank=True, null=True)
    row_index = models.IntegerField(blank=True, null=True)
    draw = models.IntegerField(blank=True, null=True)
    draw_index = models.IntegerField(blank=True, null=True, default=0)
    horse_name = models.CharField(max_length=60, blank=True, null=True)
    horse_country = models.CharField(max_length=20, blank=True, null=True)
    price_decimal = models.FloatField(blank=True, null=True)
    price_fraction = models.CharField(max_length=20, blank=True, null=True)
    price_symbol = models.CharField(max_length=20, blank=True, null=True)
    horse_age = models.IntegerField(blank=True, null=True)
    birth_year = models.IntegerField(blank=True, null=True)
    horse_weight = models.IntegerField(blank=True, null=True)
    dist_upper = models.FloatField(blank=True, null=True)
    dist_beaten = models.FloatField(blank=True, null=True)
    racecard_number = models.IntegerField(blank=True, null=True)
    horse_or = models.IntegerField(blank=True, null=True)
    horse_ts = models.IntegerField(blank=True, null=True)
    horse_rpr = models.IntegerField(blank=True, null=True)
    horse_jockey = models.CharField(max_length=80, blank=True, null=True)
    horse_trainer = models.CharField(max_length=80, blank=True, null=True)
    color = models.CharField(max_length=10, blank=True, null=True)
    sex = models.CharField(max_length=10, blank=True, null=True)
    sire = models.CharField(max_length=100, blank=True, null=True)
    sire_country = models.CharField(max_length=10, blank=True, null=True)
    dam = models.CharField(max_length=100, blank=True, null=True)
    dam_country = models.CharField(max_length=50, blank=True, null=True)
    damsire = models.CharField(max_length=100, blank=True, null=True)
    price_var = models.CharField(max_length=150, blank=True, null=True)
    headgear = models.CharField(max_length=8, blank=True, null=True)
    wind_12 = models.CharField(max_length=8, blank=True, null=True)
    horse_link = models.CharField(max_length=200, blank=True, null=True)
    racing = models.ForeignKey('General', on_delete=models.SET_NULL, blank=True, null=True)
    horse = models.ForeignKey('Horse', on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return self.sdate
    
    class Meta:
        db_table = 'ho_player'
        ordering = ('sdate', 'link', 'position')

class Horse(models.Model):
    link = models.CharField(max_length=200)
    birth_date = models.DateField(blank=True, null=True)
    owner = models.CharField(max_length=128, blank=True, null=True)
    owner_history = models.CharField(max_length=1000, blank=True, null=True)
    
    def __str__(self):
        return self.link
    
    def history_as_list(self):
        return self.owner_history.split(',')
    def horse_name(self):
        horse_name = self.link.rsplit('/', 1)[1].replace('-', ' ').title()
        return horse_name
    class Meta:
        db_table = 'ho_horse'