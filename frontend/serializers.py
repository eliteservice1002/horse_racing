from rest_framework import serializers
from .models import * 


class RacingSerializer(serializers.ModelSerializer):
    class Meta:
        model = General
        fields = '__all__'


class HorseSerializer(serializers.ModelSerializer):
    horse_name = serializers.SerializerMethodField('get_horse_name')
    class Meta:
        model = Horse
        fields = ['link', 'birth_date', 'owner', 'owner_history', 'horse_name']
    
    def get_horse_name(self, obj):
        return obj.link.rsplit('/', 1)[1].replace('-', ' ').title()

class PlayerSerializer(serializers.ModelSerializer):
    birth_date = serializers.SerializerMethodField('get_birth_date')
    class Meta:
        model = Player
        fields = '__all__'
    
    def get_birth_date(self, obj):
        return obj.horse.birth_date

class SearchSerializer(serializers.ModelSerializer):
    horse_data = HorseSerializer(many=True, read_only=True)
    general_data = RacingSerializer(many=False, read_only=True)
    birth_date = serializers.SerializerMethodField('get_birth_date')
    
    class Meta:
        model = Player
        fields = '__all__'
        depth = 2
    
    def get_birth_date(self, obj):
        return obj.horse.birth_date
    