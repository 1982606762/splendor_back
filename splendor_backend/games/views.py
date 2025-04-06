# games/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Game, Player, Card, Noble, GameLog
from .serializers import GameSerializer, PlayerSerializer

# 自定义权限类
class IsHostOrReadOnly(permissions.BasePermission):
    """只允许游戏主持人编辑游戏"""
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写入权限只允许游戏主持人
        return obj.host == request.user

class GameViewSet(viewsets.ModelViewSet):
    """处理游戏相关的所有API端点"""
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostOrReadOnly]
    
    def get_queryset(self):
        """用户只能看到自己创建或参与的游戏"""
        user = self.request.user
        return Game.objects.filter(
            Q(host=user) | Q(players__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        """创建游戏时，自动将当前用户设为主持人"""
        serializer.save(host=self.request.user)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """加入游戏的API端点"""
        game = self.get_object()
        
        # 检查游戏是否可以加入
        if not game.can_join():
            return Response(
                {"detail": "无法加入此游戏，游戏可能已开始或已满员"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查用户是否已在游戏中
        if game.players.filter(user=request.user).exists():
            return Response(
                {"detail": "您已经在此游戏中"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 添加用户到游戏
        order = game.players.count()
        player = Player.objects.create(
            user=request.user,
            game=game,
            order=order
        )
        
        return Response(PlayerSerializer(player).data)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """开始游戏的API端点"""
        game = self.get_object()
        
        # 检查是否是主持人
        if request.user != game.host:
            return Response(
                {"detail": "只有主持人可以开始游戏"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 检查游戏是否可以开始
        if not game.can_start():
            return Response(
                {"detail": "无法开始游戏，玩家数量不足"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 这里应该调用游戏初始化逻辑
        game.status = Game.PLAYING
        game.current_player = game.players.all().order_by('order').first().user
        
        # 初始化游戏状态（这部分需要根据Splendor规则实现）
        game_state = {
            'tokens': {'white': 7, 'blue': 7, 'green': 7, 'red': 7, 'black': 7, 'gold': 5},
            'cards': {
                'level1_deck': [...],  # 初始卡牌
                'level2_deck': [...],
                'level3_deck': [...],
                'board': {...}         # 展示的卡牌
            },
            'nobles': [...]            # 贵族卡牌
        }
        
        game.game_state = game_state
        game.save()
        
        return Response(GameSerializer(game).data)