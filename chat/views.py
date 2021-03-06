from rest_framework import mixins, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from tornado.websocket import WebSocketClosedError
from tornado_websockets.websocket import WebSocket

from chat.serializers import *


connected_users = {}


ws = WebSocket('/connect')


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
    return Response({'token': token.key, 'id': user_id})


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
    return chat, user


@api_view(['POST'])
def invite_user_to_chat(request, chat_id):
    chat, user = get_chat(request, chat_id)
    data = request.data
    user_id = data.get('user')
    if user_id is None:
        raise ValidationError(dict(user='This field is required'))

    invited_user = get_object_or_404(User, id=user_id)
    ChatUser.objects.create(user=invited_user, chat=chat)
    return Response()


@api_view(['GET'])
def get_messages(request, chat_id):
    chat, user = get_chat(request, chat_id)
    join_date = chat.chatuser_set.get(user=user).join_date
    paginator = PageNumberPagination()
    queryset = Message.objects.filter(chat=chat, auto_date__gt=join_date)
    context = paginator.paginate_queryset(queryset, request)
    messages = MessageSerializer(context, many=True)
    return paginator.get_paginated_response(messages.data)


@api_view(['POST'])
def send_message(request, chat_id):
    chat, user = get_chat(request, chat_id)
    data = request.data
    message = create_object(MessageSerializer, data, chat=chat, user=user)
    chat.last_date = message.data['auto_date']
    chat.last_message = get_object_or_404(Message, id=message.data['id'])
    chat.save()

    # WebSocket
    chat_users = chat.users.all()
    for chat_user in chat_users:
        sock = connected_users.get(chat_user.id)
        if sock is None:
            continue
        try:
            sock.emit('on_message', message.data)
        except WebSocketClosedError:
            del connected_users[chat_user.id]

    return Response(message.data)


"""
WebSockets
"""


@ws.on
def on_open(socket, data):
    socket.emit('success_auth', {})


@ws.on
def auth(socket, data):
    print(data)
    user_id = data.get('id')
    if user_id is None:
        socket.emit('error', {'detail': '"id" is required'})
        return
    connected_users[user_id] = socket
