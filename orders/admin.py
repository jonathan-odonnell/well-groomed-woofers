from django.contrib import admin
from .models import Order, OrderLineItem
from services.models import Appointment


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)
    extra = 1


class AppointmentmAdminInline(admin.StackedInline):
    model = Appointment
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline, AppointmentmAdminInline)

    readonly_fields = ('order_number', 'date', 'order_total',
                       'discount', 'grand_total', 'stripe_pid')

    fields = ('order_number', 'user_profile', 'date', 'full_name',
              'email', 'phone_number', 'address_line_1', 'address_line_2',
              'town_or_city',  'county', 'postcode', 'country', 'order_total',
              'discount', 'grand_total', 'stripe_pid')

    list_display = ('order_number', 'date', 'full_name', 'grand_total',)


admin.site.register(Order, OrderAdmin)
