#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout

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