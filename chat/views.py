from rest_framework import mixins, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from chat.serializers import *


@api_view(['POST'])
@permission_classes((AllowAny,))
def register(request):
    data = request.data
    user = UserSerializer(data=data)
    user.is_valid(raise_exception=True)
    user.save()
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


@api_view(['POST'])
def invite_user_to_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    request_user = request.user

    try:
        request_user.chat_set.get(id=chat_id)
    except Chat.DoesNotExist:
        raise PermissionDenied

    data = request.data
    user_id = data.get('user')
    if user_id is None:
        raise ValidationError(dict(user='This field is required'))

    user = get_object_or_404(User, id=user_id)
    ChatUser.objects.create(user=user, chat=chat)
    return Response()


@api_view(['POST'])
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    user = request.user

    try:
        user.chat_set.get(id=chat_id)
    except Chat.DoesNotExist:
        raise PermissionDenied

    data = request.data
    message = MessageSerializer(data=data)
    message.is_valid(raise_exception=True)
    message.save(chat=chat, user=request.user)
    return Response(message.data)
