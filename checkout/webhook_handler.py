from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import localdate, localtime, now
from services.models import Service, Price, Appointment
from orders.models import Order, OrderLineItem, Coupon
from profiles.models import UserProfile
import time
import json


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        coupon = intent.metadata.coupon
        save_info = intent.metadata.save_info

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        total = round(intent.charges.data[0].amount / 100, 2)

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        username = intent.metadata.username
        profile = UserProfile.objects.get(user__username=username)
        coupon_qs = None

        if save_info:
            profile.phone_number = shipping_details.phone
            profile.address_line_1 = shipping_details.address.line1
            profile.address_line_2 = shipping_details.address.line2
            profile.town_or_city = shipping_details.address.city
            profile.county = shipping_details.address.state
            profile.country = shipping_details.address.country
            profile.postcode = shipping_details.address.postal_code
            profile.save()

        if coupon:
            current_date = localdate(now())
            coupon_qs = Coupon.objects.get(
                name=coupon,
                start_date_gte=current_date,
                end_date_lte=current_date
            )

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    address_line_1__iexact=shipping_details.address.line1,
                    address_line_2__iexact=shipping_details.address.line2,
                    town_or_city__iexact=shipping_details.address.city,
                    county__iexact=shipping_details.address.state,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    coupon=coupon_qs,
                    grand_total=total,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | \
                    SUCCESS: Verified order already in database',
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    address_line_1=shipping_details.address.line1,
                    address_line_2=shipping_details.address.line2,
                    town_or_city=shipping_details.address.city,
                    county=shipping_details.address.state,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    coupon=coupon_qs,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(
                        bag['services']).items():
                    service = Service.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        item_price = Price.objects.get(
                            service=service, size=None)
                        OrderLineItem.objects.create(
                            order=self.object,
                            service=service,
                            price=item_price.price,
                            quantity=item_data,
                        )
                    else:
                        for size, size_data in item_data.items():
                            item_price = Price.objects.get(
                                service=service, size=size)
                            OrderLineItem.objects.create(
                                order=self.object,
                                service=service,
                                size=size,
                                price=item_price.price,
                                quantity=size_data['quantity'],
                            )
                            for appointment in size_data[
                                    'appointments']:
                                appointment = Appointment.objects.get(
                                    id=appointment.keys()[0],
                                    reserved=True,
                                    confirmed=False
                                )
                                appointment.order = self.object
                                appointment.confirmed = True
                                appointment.last_updated = localtime(now())
                                appointment.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)

        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | \
                SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
