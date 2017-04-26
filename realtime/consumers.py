#!/usr/bin/env python
# -*- coding: utf-8 -*-
from channels.generic.websockets import JsonWebsocketConsumer
import socket
from realtime.models import Employee, EmployeeRegister
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, date, timedelta

class MyConsumer(JsonWebsocketConsumer):

    http_user = True
    # Set to True if you want it, else leave it out
    strict_ordering = False

    range_work = {
            'before_morning':{'in':datetime.strptime('00:00:00','%H:%M:%S').time(),'out':datetime.strptime('08:00:00','%H:%M:%S').time()},
            'morning':{'in':datetime.strptime('08:00:00','%H:%M:%S').time(),'out':datetime.strptime('12:30:00','%H:%M:%S').time()},
            'lunch':{'in':datetime.strptime('12:30:00','%H:%M:%S').time(),'out':datetime.strptime('14:00:00','%H:%M:%S').time()},
            'afternoon':{'in':datetime.strptime('14:00:00','%H:%M:%S').time(),'out':datetime.strptime('18:00:00','%H:%M:%S').time()},
            'last_afternoon':{'in':datetime.strptime('18:00:00','%H:%M:%S').time(),'out':datetime.strptime('23:59:59','%H:%M:%S').time()},
        }

    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        return ["realtime"]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        self.message.reply_channel.send({"accept": True})

    def receive(self, content, **kwargs):
        """
        Called when a message is received with decoded JSON content
        """
        # Simple echo
        card_data = str(content['card_data'].replace("'","").replace("b'",""))
        try:
            employee = Employee.objects.get(card_id = card_data)
        except:
            status = 'denied'
        else:
            if employee.status == 'granted' or employee.status == "granted_reload":
                EmployeeRegister.objects.create(employee_object=employee,date=timezone.now().date(),time = timezone.localtime(timezone.now()).time())
                status = employee.status
                content['first_name'] = employee.first_name
                content['last_name'] = employee.last_name
                content['cedula'] = employee.cedula
                content['rh'] = employee.rh
                content['cargo'] = employee.cargo
                content['photo'] = employee.get_photo()

                content['message'], content['color_message'] = self.get_message_employee(employee)

                content['entrada_am'], content['color_entrada_am'] = self.get_event_time(employee,'entrada_am')
                content['salida_am'], content['color_salida_am'] = self.get_event_time(employee,'salida_am')
                content['entrada_pm'], content['color_entrada_pm'] = self.get_event_time(employee,'entrada_pm')
                content['salida_pm'], content['color_salida_pm'] = self.get_event_time(employee,'salida_pm')

            else:
                status = 'denied'
        try:
            self.socket_send(status)
        except:
            pass
        content['status'] = status
        content['card_data'] = card_data

        self.group_send('realtime',content)

    def get_pivot(self,employee,inp,output,order):

        """
        Return object or None
        """

        now = timezone.localtime(timezone.now())
        register_objects = EmployeeRegister.objects.filter(employee_object = employee, date = now.date())
        range = Q(time__gte = inp) & Q(time__lt = output)
        pivot = None
        if order == 'min':
            try:
                pivot = register_objects.filter(range).order_by('time')[0]
            except:
                pass
        elif order == 'max':
            try:
                pivot = register_objects.filter(range).order_by('-time')[0]
            except:
                pass
        return pivot

    def get_pivot_delta(self,pivot,time_value):
        if pivot != None and time_value != None:
            if time_value > pivot.time:
                delta = datetime.combine(date.today(), time_value) - datetime.combine(date.today(), pivot.time)
            else:
                delta = datetime.combine(date.today(), pivot.time) - datetime.combine(date.today(), time_value)

            return delta
        else:
            return timedelta(0)




    def get_2pivot_delta(self,pivot1,pivot2):
        if pivot1 != None and pivot2 != None:
            if pivot1.time > pivot2.time:
                delta = datetime.combine(date.today(), pivot1.time) - datetime.combine(date.today(), pivot2.time)
            else:
                delta = datetime.combine(date.today(), pivot2.time) - datetime.combine(date.today(), pivot1.time)

            return delta
        else:
            return timedelta(0)



    def get_time_delta_string(self,seconds):
        s = seconds
        hours = s // 3600
        # remaining seconds
        s = s - (hours * 3600)
        # minutes
        minutes = s // 60
        # remaining seconds
        seconds = s - (minutes * 60)
        # total time
        return '%02s:%02s:%02s' % (hours, minutes, seconds)

    def get_event_time(self,employee,event):

        now = timezone.localtime(timezone.now())
        #now = datetime.strptime('09:50:00','%H:%M:%S')

        time_format = ''
        pivot = None

        if event == 'entrada_am':
            pivot = self.get_pivot(employee,self.range_work['before_morning']['in'],self.range_work['before_morning']['out'],'min')
            if pivot == None:
                pivot = self.get_pivot(employee,self.range_work['morning']['in'],self.range_work['morning']['out'],'min')

        elif event == 'salida_am':
            if now.time() >= self.range_work['lunch']['in']:
                pivot = self.get_pivot(employee,self.range_work['lunch']['in'],self.range_work['lunch']['out'],'min')
                if pivot == None:
                    pivot = self.get_pivot(employee,self.range_work['morning']['in'],self.range_work['morning']['out'],'max')

        elif event == 'entrada_pm':
            if now.time() >= self.range_work['afternoon']['in']:

                pivot_lunch_min = self.get_pivot(employee,self.range_work['lunch']['in'],self.range_work['lunch']['out'],'min')
                pivot_lunch_max = self.get_pivot(employee,self.range_work['lunch']['in'],self.range_work['lunch']['out'],'max')

                if pivot_lunch_min != None and pivot_lunch_max != None:
                    delta = self.get_2pivot_delta(pivot_lunch_min,pivot_lunch_max)

                    if delta.seconds >= 1800:
                        pivot = pivot_lunch_max
                    else:
                        pivot = self.get_pivot(employee,self.range_work['afternoon']['in'],self.range_work['afternoon']['out'],'min')

                else:
                    pivot = self.get_pivot(employee,self.range_work['afternoon']['in'],self.range_work['afternoon']['out'],'min')

        elif event == 'salida_pm':
            if now.time() >= self.range_work['last_afternoon']['in'] and now.time() < self.range_work['last_afternoon']['out']:
                pivot = self.get_pivot(employee,self.range_work['last_afternoon']['in'],self.range_work['last_afternoon']['out'],'max')
                if pivot == None:
                    pivot = self.get_pivot(employee,self.range_work['afternoon']['in'],self.range_work['afternoon']['out'],'max')

        if pivot != None:
            time_format = datetime.combine(date.today(), pivot.time).strftime('%H:%M:%S')

        return [time_format,'black']


    def get_message_employee(self,employee):

        now = timezone.localtime(timezone.now())
        #now = datetime.strptime('09:50:00','%H:%M:%S')


        if now.time() >= self.range_work['before_morning']['in'] and now.time() < self.range_work['before_morning']['out']:

            # si el usuario ingreso antes de la jornada de la mañana
            pivot = self.get_pivot(employee,self.range_work['before_morning']['in'],self.range_work['before_morning']['out'],'min')

            if pivot != None:
                delta = self.get_pivot_delta(pivot,self.range_work['before_morning']['out'])
                if pivot.alert:
                    return ['','black']
                else:
                    pivot.alert = True
                    pivot.save()
                    return ["Felicitaciones, ingresaste con " + self.get_time_delta_string(delta.seconds) + " de adelanto.",'black']
            else:
                return ['','black']

        elif now.time() >= self.range_work['morning']['in'] and now.time() < self.range_work['morning']['out']:

            #si el usuario ingreso despues de la jornada de la mañana
            pivot_before_morning = self.get_pivot(employee,self.range_work['before_morning']['in'],self.range_work['before_morning']['out'],'min')

            if pivot_before_morning == None:
                #si el usuario no ingreso antes de la jornada
                pivot = self.get_pivot(employee,self.range_work['morning']['in'],self.range_work['morning']['out'],'min')

                if pivot != None:
                    delta = self.get_pivot_delta(pivot,self.range_work['before_morning']['out'])
                    if pivot.alert:
                        return ['','black']
                    else:
                        pivot.alert = True
                        pivot.save()
                        return ["Ingresaste con " + self.get_time_delta_string(delta.seconds) + " de retraso.",'red']
                else:
                    return ['','black']

            else:
                return ['','black']

        elif now.time() >= self.range_work['lunch']['in'] and now.time() < self.range_work['lunch']['out']:
            #si el usuario registra eventos en el almuerzo
            return ['','black']



        elif now.time() >= self.range_work['afternoon']['in'] and now.time() < self.range_work['afternoon']['out']:
            # si registra durante la tarde
            pivot_lunch_min = self.get_pivot(employee,self.range_work['lunch']['in'],self.range_work['lunch']['out'],'min')
            pivot_lunch_max = self.get_pivot(employee,self.range_work['lunch']['in'],self.range_work['lunch']['out'],'max')

            if pivot_lunch_min != None and pivot_lunch_max != None and pivot_lunch_min != pivot_lunch_max:

                delta = self.get_2pivot_delta(pivot_lunch_min,pivot_lunch_max)

                if delta.seconds >= 1800:
                    #si se registra almuerzo por lo menos de 30 minutos
                    pivot = pivot_lunch_max
                    delta = self.get_pivot_delta(pivot,self.range_work['lunch']['out'])
                    if pivot.alert:
                        return ['','black']
                    else:
                        pivot.alert = True
                        pivot.save()
                        return ['','black']
                else:
                    #si no hay evento de por lo menos 30 minutos
                    pivot = self.get_pivot(employee,self.range_work['afternoon']['in'],self.range_work['afternoon']['out'],'min')
                    delta = self.get_pivot_delta(pivot,self.range_work['afternoon']['in'])

                    if pivot.alert:
                        return ['','black']
                    else:
                        pivot.alert = True
                        pivot.save()
                        return ["Ingresaste con " + self.get_time_delta_string(delta.seconds) + " de retraso.",'red']

            elif pivot_lunch_min == pivot_lunch_max:
                pivot = self.get_pivot(employee,self.range_work['afternoon']['in'],self.range_work['afternoon']['out'],'min')
                delta = self.get_pivot_delta(pivot,self.range_work['afternoon']['in'])

                if pivot.alert:
                    return ['','black']
                else:
                    pivot.alert = True
                    pivot.save()
                    return ["Ingresaste con " + self.get_time_delta_string(delta.seconds) + " de retraso.",'red']
            else:
                return ['','black']



        elif now.time() >= self.range_work['last_afternoon']['in'] and now.time() < self.range_work['last_afternoon']['out']:
            # si registra salida despues de la jornada
            return ['','black']




    def socket_send(self,status):
        s = socket.socket()
        s.connect(("0.0.0.0", 1234))
        s.send(status.encode())
        s.close()


    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        pass