# games/models.py
from django.db import models
from django.contrib.auth.models import User
import json
import uuid
    
class Game(models.Model):
    """游戏主模型"""
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
    
    # 游戏状态数据，以JSON格式存储
    _game_state = models.TextField(blank=True, null=True, verbose_name="游戏状态JSON")
    
    # 玩家人数限制
    min_players = models.PositiveSmallIntegerField(default=2, verbose_name="最少玩家数")
    max_players = models.PositiveSmallIntegerField(default=4, verbose_name="最多玩家数")
    
    class Meta:
        verbose_name = "游戏"
        verbose_name_plural = "游戏"
    
    @property
    def game_state(self):
        """获取游戏状态"""
        if self._game_state:
            return json.loads(self._game_state)
        return {}
    
    @game_state.setter
    def game_state(self, value):
        """设置游戏状态"""
        self._game_state = json.dumps(value)
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def get_player_count(self):
        """获取当前玩家数量"""
        return self.players.count()
    
    def can_join(self):
        """检查是否还能加入玩家"""
        return self.status == self.WAITING and self.get_player_count() < self.max_players
    
    def can_start(self):
        """检查游戏是否可以开始"""
        return self.status == self.WAITING and self.get_player_count() >= self.min_players


class Player(models.Model):
    """游戏玩家模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_players', verbose_name="用户")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players', verbose_name="游戏")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")
    
    # 玩家游戏状态，以JSON格式存储
    _player_state = models.TextField(blank=True, null=True, verbose_name="玩家状态JSON")
    
    # 玩家顺序编号
    order = models.PositiveSmallIntegerField(default=0, verbose_name="玩家顺序")
    
    class Meta:
        verbose_name = "玩家"
        verbose_name_plural = "玩家"
        unique_together = ('user', 'game')  # 一个用户在一个游戏中只能有一个玩家身份
        ordering = ['order']  # 按照顺序排序
    
    @property
    def player_state(self):
        """获取玩家状态"""
        if self._player_state:
            return json.loads(self._player_state)
        return {}
    
    @player_state.setter
    def player_state(self, value):
        """设置玩家状态"""
        self._player_state = json.dumps(value)
    
    def __str__(self):
        return f"{self.user.username} in {self.game.name}"


class GameLog(models.Model):
    """游戏日志模型，记录游戏中的每一个动作"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='logs', verbose_name="游戏")
    player = models.ForeignKey(
        Player, 
        on_delete=models.CASCADE, 
        related_name='logs', 
        null=True, 
        blank=True,
        verbose_name="玩家"
    )
    action_type = models.CharField(max_length=50, verbose_name="动作类型")
    
    # 动作数据，以JSON格式存储
    _action_data = models.TextField(blank=True, null=True, verbose_name="动作数据JSON")
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="时间戳")
    
    class Meta:
        verbose_name = "游戏日志"
        verbose_name_plural = "游戏日志"
        ordering = ['timestamp']
    
    @property
    def action_data(self):
        """获取动作数据"""
        if self._action_data:
            return json.loads(self._action_data)
        return {}
    
    @action_data.setter
    def action_data(self, value):
        """设置动作数据"""
        self._action_data = json.dumps(value)
    
    def __str__(self):
        if self.player:
            return f"{self.player.user.username} - {self.action_type} - {self.timestamp}"
        return f"System - {self.action_type} - {self.timestamp}"


class Card(models.Model):
    """宝石卡牌模型"""
    # 卡牌等级
    LEVEL_CHOICES = [
        (1, '一级卡'),
        (2, '二级卡'),
        (3, '三级卡'),
    ]
    
    # 宝石颜色
    GEM_CHOICES = [
        ('white', '白色'),
        ('blue', '蓝色'),
        ('green', '绿色'),
        ('red', '红色'),
        ('black', '黑色'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="卡牌名称")
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, verbose_name="卡牌等级")
    gem_color = models.CharField(max_length=10, choices=GEM_CHOICES, verbose_name="宝石颜色")
    prestige_points = models.PositiveSmallIntegerField(default=0, verbose_name="声望点数")
    
    # 卡牌费用 (以JSON格式存储)
    _cost = models.TextField(verbose_name="费用JSON")
    
    class Meta:
        verbose_name = "卡牌"
        verbose_name_plural = "卡牌"
    
    @property
    def cost(self):
        """获取卡牌费用"""
        return json.loads(self._cost)
    
    @cost.setter
    def cost(self, value):
        """设置卡牌费用"""
        self._cost = json.dumps(value)
    
    def __str__(self):
        return f"{self.name} (Lv.{self.level}, {self.get_gem_color_display()}, {self.prestige_points}点)"


class Noble(models.Model):
    """贵族卡牌模型"""
    name = models.CharField(max_length=100, verbose_name="贵族名称")
    prestige_points = models.PositiveSmallIntegerField(default=3, verbose_name="声望点数")
    
    # 贵族拜访要求 (以JSON格式存储)
    _requirements = models.TextField(verbose_name="要求JSON")
    
    class Meta:
        verbose_name = "贵族"
        verbose_name_plural = "贵族"
    
    @property
    def requirements(self):
        """获取贵族要求"""
        return json.loads(self._requirements)
    
    @requirements.setter
    def requirements(self, value):
        """设置贵族要求"""
        self._requirements = json.dumps(value)
    
    def __str__(self):
        return f"{self.name} ({self.prestige_points}点)"