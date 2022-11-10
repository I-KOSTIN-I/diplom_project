from django.db import transaction
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView
from rest_framework import permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment, Board
from goals.permissions import BoardPermissions, GoalCategoryPermissions, GoalPermissions, GoalCommentPermissions
from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalSerializer, \
    GoalCreateSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardSerializer, BoardCreateSerializer


class TestCreateView(CreateAPIView):
    queryset = Goal.objects.all()
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [GoalCategoryPermissions]
    serializer_class = GoalCategoryCreateSerializer


@method_decorator(csrf_exempt, name='dispatch')
class GoalCategoryCreateView2(View):
    def post(self, request):
        import json
        data = json.loads(request.body)
        user = request.user
        gc = GoalCategory(title=data['title'], board_id=data['board'], user_id=user.id)
        gc.user_id = user.id
        gc.save(force_insert=True)
        from django.http import JsonResponse
        return JsonResponse({
            "id": gc.id,
            "title": gc.title,
            "is_deleted": gc.is_deleted,
            "board": gc.board_id,
            "board_id": gc.board_id
        })


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    permission_classes = [GoalCategoryPermissions]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_field = ['board']
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
            board__participants__user_id=self.request.user.id,
            is_deleted=False
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [GoalCategoryPermissions]

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
            board__participants__user_id=self.request.user.id,
            is_deleted=False
        )

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            Goal.objects.filter(category=instance.update(status=Goal.Status.archived))
        return instance


class GoalCreateView(CreateAPIView):
    model = Goal
    serializer_class = GoalCreateSerializer
    permission_classes = [GoalPermissions]


class GoalListView(ListAPIView):
    model = Goal
    permission_classes = [GoalPermissions]
    serializer_class = GoalSerializer
    filterset_class = GoalDateFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return Goal.objects.select_related('user', 'category__board').filter(
            Q(category__board__participants__user_id=self.request.user.id)
            & ~Q(status=Goal.Status.archived)
        )


class GoalView(RetrieveUpdateAPIView):
    model = Goal
    permission_classes = [GoalPermissions]
    serializer_class = GoalSerializer

    def get_queryset(self):
        return Goal.objects.select_related('user', 'category__board').filter(
            Q(category__board__participants__user_id=self.request.user.id)
            & ~Q(status=Goal.Status.archived)
        )

    def perform_destroy(self, instance: Goal):
        instance.status = Goal.Status.archived
        instance.save(update_fields=('status',))
        return instance


class GoalCommentCreateView(CreateAPIView):
    serializer_class = GoalCommentCreateSerializer
    permission_classes = [GoalCommentPermissions]


class GoalCommentListView(ListAPIView):
    model = GoalComment
    permission_classes = [GoalCommentPermissions]
    serializer_class = GoalCommentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.select_related('goal__category__board', 'user').filter(
            user_id=self.request.user.id,
            goal__category__board__participants__user_id=self.request.user.id
        )


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    permission_classes = [GoalCommentPermissions]
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        return GoalComment.objects.select_related('goal__category__board', 'user').filter(
            user_id=self.request.user.id,
            goal__category__board__participants__user_id=self.request.user.id
        )


class BoardView(RetrieveUpdateDestroyAPIView):
    model = Board
    permission_classes = [BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        # Обратите внимание на фильтрацию – она идет через participants
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: Board):
        # При удалении доски помечаем ее как is_deleted,
        # «удаляем» категории, обновляем статус целей
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )
        return instance


class BoardCreateView(CreateAPIView):
    model = Board
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardCreateSerializer


class BoardListView(ListAPIView):
    model = Board
    permission_classes = [BoardPermissions]
    serializer_class = BoardSerializer
    ordering = ['title']

    def get_queryset(self):
        # Обратите внимание на фильтрацию – она идет через participants
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)
