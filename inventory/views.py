import os

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from inventory.forms import (
    IssueForm,
    ReceiveForm,
    ReorderLevelForm,
    StockCreateForm,
    StockHistorySearchForm,
    StockSearchForm,
    StockUpdateForm,
)
from inventory.models import Stock
from inventory.repositories import history_repo, stock_repo
from inventory.services import export_service, stock_service
from stock.exceptions import StockException


@login_required
def view_stock(request):
    title = 'VIEW STOCKS'
    everything = stock_repo.get_all()
    form = StockSearchForm(request.POST or None)

    context = {'everything': everything, 'form': form}
    if request.method == 'POST':
        category = form['category'].value()
        category_id = int(category) if category else None
        everything = stock_repo.search(
            item_name=form['item_name'].value(),
            category_id=category_id,
        )
        if form['export_to_CSV'].value() == True:
            resp = HttpResponse(content_type='text/csv')
            resp['Content-Disposition'] = 'attachment; filename = "Invoice.csv"'
            resp.write(export_service.export_stocks_to_csv(everything))
            return resp
        context = {'title': title, 'everything': everything, 'form': form}
    return render(request, 'stock/view_stock.html', context)


@login_required
def add_stock(request):
    title = 'Add Stock'
    add = Stock.objects.all()
    form = StockCreateForm
    if request.method == 'POST':
        form = StockCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successful')
            return redirect(reverse('view_stock'))
    context = {'add': add, 'form': form, 'title': title}
    return render(request, 'stock/add_stock.html', context)


@login_required
def update_stock(request, pk):
    title = 'Update Stock'
    update = get_object_or_404(Stock, id=pk)
    form = StockUpdateForm(instance=update)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, request.FILES, instance=update)
        if form.is_valid():
            if update.image and hasattr(update.image, 'path'):
                image_path = update.image.path
                if os.path.exists(image_path):
                    os.remove(image_path)
            form.save()
            messages.success(request, 'Successfully Updated!')
            return redirect(reverse('view_stock'))
    context = {'form': form, 'update': update, 'title': title}
    return render(request, 'stock/add_stock.html', context)


@login_required
def delete_stock(request, pk):
    get_object_or_404(Stock, id=pk).delete()
    messages.success(request, 'Your file has been deleted.')
    return redirect(reverse('view_stock'))


@login_required
def stock_detail(request, pk):
    detail = get_object_or_404(Stock, id=pk)
    context = {'detail': detail}
    return render(request, 'stock/stock_detail.html', context)


@login_required
def issue_item(request, pk):
    issue = get_object_or_404(Stock, id=pk)
    form = IssueForm(request.POST or None, instance=issue)
    if form.is_valid():
        quantity = form.cleaned_data.get('issue_quantity')
        issued_to = form.cleaned_data.get('issued_to_person')
        try:
            value = stock_service.issue_stock(stock=issue, quantity=quantity, issued_by=request.user, issued_to=issued_to)
            messages.success(
                request,
                'Issued Successfully, ' + str(value.quantity) + ' ' + str(value.item_name) + 's now left in Store',
            )
        except (ValidationError, StockException) as exc:
            messages.error(request, str(exc))
        return redirect(reverse('stock_detail', args=[issue.id]))

    context = {
        'title': 'Issue ' + str(issue.item_name),
        'issue': issue,
        'form': form,
        'username': 'Issued by: ' + str(request.user),
    }
    return render(request, 'stock/add_stock.html', context)


@login_required
def receive_item(request, pk):
    receive = get_object_or_404(Stock, id=pk)
    form = ReceiveForm(request.POST or None, instance=receive)
    if form.is_valid():
        quantity = form.cleaned_data.get('receive_quantity')
        try:
            value = stock_service.receive_stock(stock=receive, quantity=quantity, received_by=request.user)
            messages.success(
                request,
                'Received Successfully, ' + str(value.quantity) + ' ' + str(value.item_name) + 's now in Store',
            )
        except (ValidationError, StockException) as exc:
            messages.error(request, str(exc))

        return redirect(reverse('stock_detail', args=[receive.id]))
    context = {
        'title': 'Receive ' + str(receive.item_name),
        'receive': receive,
        'form': form,
        'username': 'Received by: ' + str(request.user),
    }
    return render(request, 'stock/add_stock.html', context)


@login_required
def re_order(request, pk):
    order = get_object_or_404(Stock, id=pk)
    form = ReorderLevelForm(request.POST or None, instance=order)
    if form.is_valid():
        reorder_level = form.cleaned_data.get('re_order')
        try:
            value = stock_service.update_reorder_level(stock=order, reorder_level=reorder_level)
            messages.success(request, 'Reorder level for ' + str(value.item_name) + ' is updated to ' + str(value.re_order))
        except (ValidationError, StockException) as exc:
            messages.error(request, str(exc))
        return redirect(reverse('view_stock'))
    context = {
        'value': order,
        'form': form,
    }
    return render(request, 'stock/add_stock.html', context)


@login_required
def view_history(request):
    title = 'STOCK HISTORY'
    history = history_repo.get_all()
    form = StockHistorySearchForm(request.POST or None)
    context = {
        'title': title,
        'history': history,
        'form': form,
    }
    if request.method == 'POST':
        category = form['category'].value()
        category_id = int(category) if category else None
        history = history_repo.search(
            item_name=form['item_name'].value(),
            category_id=category_id,
            start_date=form['start_date'].value(),
            end_date=form['end_date'].value(),
        )

        if form['export_to_CSV'].value() == True:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
            response.write(export_service.export_history_to_csv(history))
            return response
        context = {
            'form': form,
            'title': title,
            'history': history,
        }
    return render(request, 'stock/view_history.html', context)
