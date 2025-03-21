from django.contrib import admin
from .models import Game, Player, Card, Noble, GameLog
# Register your models here.

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'status', 'current_player', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['id', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'game', 'user', 'score']
    list_filter = ['game', 'score']
    search_fields = ['id', 'game', 'user']
    readonly_fields = ['id']