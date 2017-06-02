#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from realtime.models import Employee

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
    def post(self, request, format=None):

        status = 'denied'

        if 'card_data' in request.data.keys():

            try:
                employee = Employee.objects.get(card_id = request.data['card_data'])
            except:
                pass
            else:
                if employee.status == 'granted' or employee.status == "granted_reload":
                    status = 'granted'

        return Response({'status':status})