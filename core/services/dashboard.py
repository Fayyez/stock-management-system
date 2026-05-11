from django.db.models import Q

from core.models import User
from inventory.models import Category, Stock


def build_dashboard_context(client_ip: str):
    """Build dashboard counters and chart arrays for home view."""
    labels = []
    label_item = []
    data = []
    issue_data = []
    receive_data = []

    user_obj = User(user=client_ip)
    result = User.objects.filter(Q(user__icontains=client_ip))
    if len(result) != 1:
        user_obj.save()

    queryset = Stock.objects.all()
    querys = Category.objects.all()

    for chart in queryset:
        label_item.append(chart.item_name)
        data.append(chart.quantity)
        issue_data.append(chart.issue_quantity)
        receive_data.append(chart.receive_quantity)

    for chart in querys:
        labels.append(str(chart.group))

    return {
        'count': User.objects.all().count(),
        'body': Category.objects.values('stock').count(),
        'mind': Category.objects.values('stockhistory').count(),
        'soul': Category.objects.values('group').count(),
        'labels': labels,
        'data': data,
        'issue_data': issue_data,
        'receive_data': receive_data,
        'label_item': label_item,
    }
