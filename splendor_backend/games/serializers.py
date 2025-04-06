# games/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Game, Player, Card, Noble, GameLog

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        # 不包含密码等敏感字段

class GameSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)  # 嵌套序列化器
    current_player = UserSerializer(read_only=True)
    winner = UserSerializer(read_only=True)
    
    class Meta:
        model = Game
        fields = [
            'id', 'name', 'created_at', 'updated_at', 'status', 
            'host', 'current_player', 'winner', 'game_state',
            'min_players', 'max_players'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Player
        fields = ['id', 'user', 'game', 'score', 'order', 'is_current', 'is_winner', 'joined_at', 'player_state']