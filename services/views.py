from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.timezone import make_aware, get_current_timezone
from .models import Service, Availability
from checkout.models import Appointment
from .forms import ServiceForm
from .utils import SuperUserRequired
from datetime import datetime, date, timedelta
import calendar
from calendar import Calendar


class ServicesView(ListView):
    model = Service
    context_object_name = 'services'
    template_name = 'services/services.html'


class AppointmentsView(LoginRequiredMixin, DetailView):
    model = Service
    context_object_name = 'service'
    template_name = 'services/appointments.html'

    def get_context_data(self, month=None, year=None, **kwargs):
        context = super().get_context_data(**kwargs)
        day = 1

        if not month:
            current_date = date.today()
            day = current_date.day
            month = current_date.month
            year = current_date.year

        num_days = calendar.monthrange(year, month)[1]
        classes = []

        for i in range(1, num_days + 1):
            day_date = date(year, month, i)
            appointments = self.get_appointments(day_date)
            if i >= day and len(appointments) == 1:
                classes.append('availability-1')
            elif i >= day and len(appointments) == 2:
                classes.append('availability-2')
            elif i >= day and len(appointments) == 3:
                classes.append('availability-3')
            else:
                classes.append('disabled')

        context['calendar'] = Calendar(6).monthdayscalendar(year, month)
        context['classes'] = classes
        context['month'] = calendar.month_name[month]
        context['year'] = year
        return context

    def get_appointments(self, date):
        availability = Availability.objects.get(
            start_date__lte=date, end_date__gte=date)
        appointments = ['10:00', '13:00', '15:00']
        appointments_start = make_aware(datetime.combine(
            date, availability.start_time))
        appointments_end = make_aware(datetime.combine(
            date, availability.end_time))
        booked_appointments = Appointment.objects.filter(
            start__gte=appointments_start,
            end__lte=appointments_end
        )

        for appointment in appointments:
            appointment_start = datetime.strptime(appointment, '%H:%M').time()
            appointment_end = (datetime.strptime(
                appointment, '%H:%M') + timedelta(hours=2)).time()
            if (appointment_start <= availability.start_time
                    or appointment_end > availability.end_time):
                appointments.remove(appointment)

        for appointment in booked_appointments:
            appointment = appointment.start.astimezone(
                get_current_timezone()).strftime('%H:%M')
            if appointment in appointments:
                appointments.remove(appointment)

        return appointments

    def get(self, request, pk, month=None, year=None):
        self.object = self.get_object()
        context = self.get_context_data(month, year)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'calendar': context['calendar'],
                'classes': context['classes'],
                'month': context['month'],
                'year': context['year'],
            })
        else:
            return self.render_to_response(context)

    def post(self, request, pk):
        date = make_aware(datetime.strptime(
            request.POST['date'], '%d/%m/%Y'))
        appointments = self.get_appointments(date)
        return JsonResponse({'appointments': appointments})


class AddServiceView(LoginRequiredMixin, SuperUserRequired, CreateView):
    model = Service
    form_class = ServiceForm
    context_object_name = 'service'
    template_name = 'services/add_service.html'
    success_url = reverse_lazy('services')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Successfully added service!')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Failed to add service. \
            Please ensure the form is valid.')
        return self.render_to_response(self.get_context_data())


class EditServiceView(LoginRequiredMixin, SuperUserRequired, UpdateView):
    model = Service
    form_class = ServiceForm
    context_object_name = 'service'
    template_name = 'services/edit_service.html'
    success_url = reverse_lazy('services')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Successfully updated service!')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Failed to update service. \
            Please ensure the form is valid.')
        return self.render_to_response(self.get_context_data())


class DeleteServiceView(LoginRequiredMixin, SuperUserRequired, DeleteView):
    model = Service
    success_url = reverse_lazy('services')
    http_method_names = ['POST']

    def form_valid(self, form):
        self.object.delete()
        messages.success(self.request, 'Successfully deleted service!')
        return redirect(self.get_success_url())
