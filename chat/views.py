from rest_framework import mixins
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from chat.serializers import *


@api_view(['POST'])
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
