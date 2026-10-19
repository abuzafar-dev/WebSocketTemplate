from django.urls import path

from chat import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/<slug:room_name>/', views.room, name='room'),
]
