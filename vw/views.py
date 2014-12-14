from vw.invoice_to_stock_movement import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from stock.views import ManualStockMovementCreateView, ManualStockMovement
from vw.forms import VWManualStockMovementForm


@login_required()
def VWHomeView(request):
    return render(request, 'vw/dashboard.html')


class VWManualStockMovementCreateView(ManualStockMovementCreateView):
    model = ManualStockMovement
    form_class = VWManualStockMovementForm
    template_name = 'vw/release-stock-without-invoice.html'


@login_required()
def newVWInvoiceINView(request):
    shortcuts.initialiseMerchandiserSession(request)
    distributors = Brand.getUniqueDistributors()
    stores = Store.objects.all()
    context = {
        'distributors': distributors,
        'stores': stores,
    }
    return render(request, 'vw/new-invoice-stock-movement-in.html', context)


@login_required()
def newVWInvoiceOUTView(request):
    distributors = Brand.getUniqueDistributors()
    stores = Store.objects.all()
    context = {
        'distributors': distributors,
        'stores': stores,
    }
    return render(request, 'vw/new-invoice-stock-movement-out.html', context)