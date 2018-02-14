from django.conf.urls import url
from django.urls import include
from rest_framework.authtoken import views as auth_views
from rest_framework.routers import DefaultRouter

from chat import views

router = DefaultRouter()
router.register('users', views.UserViewSet)
router.register('chats', views.ChatViewSet, base_name='chats')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^login/', auth_views.obtain_auth_token),
    url(r'^register/', views.register),
    url(r'chats/(?P<chat_id>[0-9]+)/invite/', views.invite_user_to_chat),
]
