from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from realtime import views

urlpatterns = [
    url(r'^$', views.LoginView.as_view()),
    url(r'^logout/', views.LogoutView.as_view()),
    url(r'^inicio/', login_required(views.InicioView.as_view())),
    url(r'^window/', views.WindowView.as_view()),
    url(r'^status/$', views.StatusView.as_view()),
]