from django.shortcuts import get_object_or_404
from services.models import Service
from decimal import Decimal
from datetime import date


def bag_contents(request):
    services = []
    order_total = 0
    grand_total = 0
    discount = 0
    item_count = 0
    bag = request.session.get('bag', {})
    coupon = request.session.get('coupon', '')

    for item_id, item_quantity in bag.items():
        service = get_object_or_404(Service, id=item_id)
        order_total += item_quantity * service.price
        item_count += item_quantity
        services.append({
            'item_id': item_id,
            'quantity': item_quantity,
            'service': service,
        })

    if coupon:
        current_date = date.today()
        coupon_qs = get_object_or_404(
            name=coupon,
            start_date_gte=current_date,
            end_date_lte=current_date)
        discount = coupon_qs.amount

    order_total = Decimal(order_total * 0.8)
    tax = Decimal(order_total * 0.2)
    grand_total = Decimal(order_total + tax - discount)

    context = {
        'services': services,
        'order_total': order_total,
        'coupon': coupon,
        'discount': discount,
        'tax': tax,
        'grand_total': grand_total,
        'item_count': item_count,
    }

    return context
