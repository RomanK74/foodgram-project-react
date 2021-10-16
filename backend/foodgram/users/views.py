from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import (ChangePasswordSerializer, RecipeAuthorSerializer,
                          SubscribeSerializer, UserDetailSerializer,
                          UserRegistrationSerializer)

SUBSCRIBE_CREATE_MESSAGE = 'Вы подписались на автора'
SUBSCRIBE_DELETE_MESSAGE = 'Вы отписались от автора'
SET_PASSWORD_MESSAGE = 'Пароль успешно изменен'


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserDetailSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        user = request.user
        context = {'request': request}
        serializer = UserDetailSerializer(
            user,
            context=context
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        data = {'user': request.user.id,
                'author': pk}
        serializer = SubscribeSerializer(data=data)
        if request.method == 'GET':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'status': SUBSCRIBE_CREATE_MESSAGE},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            serializer.is_valid(raise_exception=True)
            unfollow = get_object_or_404(
                Subscription, **serializer.validated_data)
            unfollow.delete()
            return Response(
                {'status': SUBSCRIBE_DELETE_MESSAGE},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        context = {'request': request}
        subscriber = User.objects.filter(
            author__in=request.user.author.all()
        ).order_by("id")
        page = self.paginate_queryset(subscriber)
        if page:
            serializer = RecipeAuthorSerializer(
                page,
                many=True,
                context=context
            )
            return self.get_paginated_response(serializer.data)
        serializer = RecipeAuthorSerializer(
            subscriber,
            many=True,
            context=context
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'status': SET_PASSWORD_MESSAGE},
            status=status.HTTP_201_CREATED
        )
