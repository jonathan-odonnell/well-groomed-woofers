from django.urls.base import reverse
from django.views.generic.base import View, TemplateView
from django.shortcuts import redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from pets.models import Pet
from services.models import Service, Appointment
from datetime import datetime
from django.utils.timezone import make_aware, localtime, now


class BagView(TemplateView):
    template_name = "bag/bag.html"


class AddServiceToBagView(View):
    """ Add the specified service to the shopping bag """
    http_method_names = ['post']

    def post(self, request, item_id):
        service = get_object_or_404(Service, id=item_id)
        bag = request.session.get('bag', {'services': {}})
        size = Pet.objects.get(id=request.POST['pet']).get_size()
        start_time = make_aware(datetime.strptime(
            request.POST['appointment'], '%d/%m/%Y %H:%M'))

        try:
            appointment = Appointment.objects.get(
                start_time=start_time, confirmed=False)
            appointment.reserved = True
            appointment.comments = request.POST['comments']
            appointment.last_updated = localtime(now())
            appointment.save()

            if item_id in list(bag['services'].keys()):
                if size in bag['services'][item_id].keys():
                    bag['services'][item_id][size]['quantity'] += 1
                    bag['services'][item_id][size]['appointments'].append(
                        appointment.id)
                    messages.success(
                        request, f'Added {service.name} for {size} dog to bag')
                else:
                    bag['services'][item_id][size] = {
                        'quantity': 1,
                        'appointments': [appointment.id]
                    }
                    messages.success(
                        request, f'Added {service.name} for {size} dog to bag')
            else:
                bag['services'][item_id] = {size: {
                    'quantity': 1,
                    'appointments': [appointment.id]
                }}
                messages.success(
                    request, f'Added {service.name} for {size} dog to bag')

            request.session['bag'] = bag
            return redirect(reverse('services'))

        except Appointment.DoesNotExist:
            messages.success(
                request, 'Appointment is no longer available. \
                    Please try again.')
            return redirect(request.META.get('HTTP_REFERER'))


class RemoveServiceFromBagView(View):
    """ Removes the specified service from the shopping bag """
    http_method_names = ['post']

    def post(self, request, item_id):
        try:
            bag = request.session.get('bag', {})
            size = request.POST['size']
            appointment = int(request.POST['appointment'])
            bag['services'][item_id][size]['quantity'] -= 1
            bag['services'][item_id][size]['appointments'].remove(appointment)

            if bag['services'][item_id][size]['quantity'] == 0:
                bag['services'][item_id].pop(size)

            if not bag['services'][item_id]:
                bag['services'].pop(item_id)

            appointment = Appointment.objects.get(id=appointment)
            appointment.comments = None
            appointment.reserved = False
            appointment.last_updated = None
            appointment.save()
            request.session['bag'] = bag
            bag_content = render_to_string('bag/bag-content.html', {}, request)
            return JsonResponse({'bag_content': bag_content})
        except Exception as e:
            messages.error(request, f'Error removing item: {e}')
            return HttpResponse(status=500)
