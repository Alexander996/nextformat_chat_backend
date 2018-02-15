from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from chat import views
from chat.utils import AuthToken

router = DefaultRouter()
router.register('users', views.UserViewSet)
router.register('chats', views.ChatViewSet, base_name='chats')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^login/', AuthToken.as_view()),
    url(r'^register/', views.register),
    url(r'chats/(?P<chat_id>[0-9]+)/invite/', views.invite_user_to_chat),
    url(r'chats/(?P<chat_id>[0-9]+)/messages/', views.get_messages),
    url(r'chats/(?P<chat_id>[0-9]+)/send_message/', views.send_message),
]
