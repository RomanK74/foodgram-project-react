from rest_framework.decorators import action
from rest_framework import (permissions,
                            viewsets, status)
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import User, Subscribtion
from .serializers import (
    RecipeAuthorSerializer,
    SubscribeSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    ChangePasswordSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return User

    @action(
        detail=True,
        methods=['GET', 'PATH', 'PUT'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
            serializer.is_valid()
            serializer.save()
            return Response(
                {'status': 'Вы подписались на автора'},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            unfollow = get_object_or_404(
                Subscribtion, **serializer.validated_data)
            unfollow.delete()
            return Response(
                {'status': 'Вы отписались от автора'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriber = User.objects.filter(author__user__id=request.user.id)
        page = self.paginate_queryset(subscriber)
        if page:
            serializer = RecipeAuthorSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = RecipeAuthorSerializer(
            subscriber,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = ChangePasswordSerializer(
            deta=request.date, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'status': 'Пароль успешно изменен'},
            status=status.HTTP_201_CREATED
        )
