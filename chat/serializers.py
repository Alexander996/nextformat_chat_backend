from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from chat.models import *


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create(password=make_password(password), **validated_data)


class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatUser
        exclude = ('chat', 'id')

    def to_representation(self, instance):
        ret = super(ChatUserSerializer, self).to_representation(instance)
        ret['user'] = UserSerializer().to_representation(instance.user)
        return ret


class ChatSerializer(serializers.ModelSerializer):
    users = ChatUserSerializer(source='chatuser_set', many=True)

    class Meta:
        model = Chat
        fields = '__all__'

    def create(self, validated_data):
        users = validated_data.pop('chatuser_set')
        if not users:
            raise ValidationError(dict(detail='users can not be empty'))

        chat = Chat.objects.create(**validated_data)
        for user in users:
            ChatUser.objects.create(**user, chat=chat)
        return chat

    def to_representation(self, instance):
        ret = super(ChatSerializer, self).to_representation(instance)
        user_list = []
        users = ret['users']
        for user in users:
            user_list.append(user['user'])
        ret['users'] = user_list
        return ret
