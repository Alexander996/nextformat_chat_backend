from rest_framework import mixins, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from chat.serializers import *


def create_object(serializer, data, **kwargs):
    obj = serializer(data=data)
    obj.is_valid(raise_exception=True)
    obj.save(**kwargs)
    return obj


@api_view(['POST'])
@permission_classes((AllowAny,))
def register(request):
    data = request.data
    user = create_object(UserSerializer, data)
    user_id = user.data['id']
    token, created = Token.objects.get_or_create(user=get_object_or_404(User, pk=user_id))
    return Response({'token': token.key})


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(chatuser__user=self.request.user)


def check_user_chat_permissions(chat, user):
    try:
        user.chat_set.get(id=chat.id)
    except Chat.DoesNotExist:
        raise PermissionDenied


def get_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    user = request.user
    check_user_chat_permissions(chat, user)
    return chat


@api_view(['POST'])
def invite_user_to_chat(request, chat_id):
    chat = get_chat(request, chat_id)
    data = request.data
    user_id = data.get('user')
    if user_id is None:
        raise ValidationError(dict(user='This field is required'))

    invited_user = get_object_or_404(User, id=user_id)
    ChatUser.objects.create(user=invited_user, chat=chat)
    return Response()


@api_view(['GET'])
def get_messages(request, chat_id):
    chat = get_chat(request, chat_id)
    paginator = PageNumberPagination()
    queryset = Message.objects.filter(chat=chat)
    context = paginator.paginate_queryset(queryset, request)
    messages = MessageSerializer(context, many=True)
    return paginator.get_paginated_response(messages.data)


@api_view(['POST'])
def send_message(request, chat_id):
    chat = get_chat(request, chat_id)
    user = request.user
    data = request.data
    message = create_object(MessageSerializer, data, chat=chat, user=user)
    return Response(message.data)
