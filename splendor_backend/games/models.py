from django.db import models
import json
import uuid
from django.contrib.auth.models import User
# Create your models here.


class Game(models.Model):
    WAITING = 'waiting'
    PLAYING = 'playing'
    FINISHED = 'finished'

    STATUS_CHOICES = [
        (WAITING, '等待玩家加入'),
        (PLAYING, '游戏进行中'),
        (FINISHED, '游戏已结束'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="游戏名称")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=WAITING, verbose_name="游戏状态")
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_games', verbose_name="房主")
    current_player = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='turn_games',
        verbose_name="当前玩家"
    )
    winner = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='won_games',
        verbose_name="获胜者"
    )

    _game_state = models.TextField(blank=True, null=True, verbose_name="游戏状态JSON")

    min_players = models.PositiveSmallIntegerField(default=2, verbose_name="最少玩家数")
    max_players = models.PositiveSmallIntegerField(default=4, verbose_name="最多玩家数")

    class Meta:
        verbose_name = "游戏"
        verbose_name_plural = "游戏"
        
    @property
    def game_state(self):
        """
        获取游戏状态
        """
        if self._game_state:
            return json.loads(self._game_state)
        return {}
    
    @game_state.setter
    def game_state(self, value):
        """
        设置游戏状态
        """
        self._game_state = json.dumps(value)
    
    def __str__(self):
        return f"{self.name} ({self.status})"
    
    def get_player_count(self):
        """
        获取玩家数量
        """
        return self.players.count()
    
    def can_join(self):
        """
        判断是否可以加入游戏
        """
        return self.status == Game.WAITING and self.get_player_count() < self.max_players
    
    def can_start(self):
        """
        判断是否可以开始游戏
        """
        return self.status == Game.WAITING and self.get_player_count() >= self.min_players
    

class Player(models.Model):
    """Player model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='players', verbose_name="用户")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players', verbose_name="游戏")
    score = models.PositiveIntegerField(default=0, verbose_name="分数")
    order = models.PositiveSmallIntegerField(verbose_name="玩家顺序")
    is_current = models.BooleanField(default=False, verbose_name="是否当前玩家")
    is_winner = models.BooleanField(default=False, verbose_name="是否获胜者")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")
    _player_state = models.JSONField(blank=True, null=True, verbose_name="玩家状态")


    class Meta:
        verbose_name = "玩家"
        verbose_name_plural = "玩家"
        ordering = ['order']

    @property
    def player_state(self):
        """
        获取玩家状态
        """
        if self._player_state:
            return json.loads(self._player_state)
        return {}
    
    @player_state.setter
    def player_state(self, value):
        """
        设置玩家状态
        """
        self._player_state = json.dumps(value)

    def __str__(self):
        return f"{self.user.username} ({self.game.name})"
    

class Card(models.Model):
    """Card model"""
    LEVEL_CHOICES = [
        (1, '一级'),
        (2, '二级'),
        (3, '三级'),
    ]

    COLOR_CHOICES = [
        ('white', '钻石'),
        ('blue', '蓝宝石'),
        ('green', '绿翡翠'),
        ('red', '红宝石'),
        ('black', '黑宝石'),
        ('gold', '金币'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, verbose_name="等级")
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, verbose_name="颜色")
    points = models.PositiveSmallIntegerField(verbose_name="分数")
    _cost = models.JSONField(verbose_name="花费")

    class Meta:
        verbose_name = "卡牌"
        verbose_name_plural = "卡牌"
    
    @property
    def cost(self):
        return json.loads(self._cost)
    
    @cost.setter
    def cost(self, value):
        self._cost = json.dumps(value)


    def __str__(self):
        return f"{self.color} {self.level} ({self.points})"
    
class Noble(models.Model):
    """Noble model"""
    name = models.CharField(max_length=100, verbose_name="贵族名称")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    points = models.PositiveSmallIntegerField(verbose_name="分数")
    requirement = models.JSONField(verbose_name="需求", default=dict)

    class Meta:
        verbose_name = "贵族"
        verbose_name_plural = "贵族"
    
    def __str__(self):
        return f"{self.name} ({self.points})"
    


class GameLog(models.Model):
    """GameLog model"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='logs', verbose_name="游戏")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='logs', verbose_name="玩家")
    action = models.CharField(max_length=100, verbose_name="动作")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")


    class Meta:
        verbose_name = "游戏日志"
        verbose_name_plural = "游戏日志"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} ({self.created_at})"