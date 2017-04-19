from django.conf.urls import url
from realtime import views

urlpatterns = [

    url(r'^$', views.LoginView.as_view()),
    url(r'^logout/', views.LogoutView.as_view()),
]