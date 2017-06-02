#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from realtime.models import Employee
import time
import RPi.GPIO as GPIO

class LoginView(TemplateView):
    template_name = 'realtime/login.html'

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated():
            return redirect('/inicio/')
        else:
            if request.method == 'GET':
                context = self.get_context_data(**kwargs)
                return self.render_to_response(context)

            elif request.method == 'POST':
                context = self.get_context_data(**kwargs)
                email = request.POST['email']
                password = request.POST['password']

                user = authenticate(username=email,password=password)

                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('/inicio/')
                    else:
                        context['error'] = "Tu usuario no se encuentra activo."
                        context['email'] = email
                        return self.render_to_response(context)
                else:
                    context['error'] = "El correo electrónico y la contraseña que ingresaste no coinciden."
                    context['email'] = email
                    return self.render_to_response(context)

            else:
                return super(LoginView,self).dispatch(request, *args, **kwargs)

class LogoutView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')

class InicioView(TemplateView):
    template_name = 'realtime/inicio.html'

class WindowView(TemplateView):
    template_name = 'realtime/window.html'



class StatusView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    green = 24
    red = 23
    relay = 18
    delay = 2

    def setup(self):
        GPIO.setwarnings(False)
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.green, GPIO.OUT)
        GPIO.setup(self.red, GPIO.OUT)
        GPIO.setup(self.relay, GPIO.OUT)

    def handle(self, status):
        if status == "granted":
            self.signal_gpio(self.green,True)
            self.signal_gpio(self.red,False)
            self.signal_gpio(self.relay,True)

        elif status == "close":
            self.signal_gpio(self.green,False)
            self.signal_gpio(self.red,False)
            self.signal_gpio(self.relay,False)

        elif status == "denied":
            self.signal_gpio(self.green,False)
            self.signal_gpio(self.red,True)
            self.signal_gpio(self.relay,False)


    def signal_gpio(self, gpio, status):
        GPIO.output(gpio, status)

    def post(self, request, format=None):

        self.setup()
        status = 'denied'

        if 'card_data' in request.data.keys():

            try:
                employee = Employee.objects.get(card_id = request.data['card_data'])
            except:
                self.handle('denied')
                time.sleep(2)
                self.handle('close')
            else:
                if employee.status == 'granted' or employee.status == "granted_reload":
                    status = 'granted'
                    self.handle('granted')
                    time.sleep(2)
                    self.handle('close')

        return Response({'status':status})

