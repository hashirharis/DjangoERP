# Create your views here.
from django.shortcuts import render, HttpResponse, Http404, HttpResponseRedirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.utils import timezone
from django.views.generic import CreateView, UpdateView

from brutils.shortcuts import paginate_queryset
from brutils.generic.views import LoginRequiredMixin

from bulletins.models import *
from bulletins.forms import BulletinForm, PromotionForm
from lib.jsonStringify.collation import collationFromJson, jsonFromCollation, updateOrders
from users.models import Store

import json
import csv

@login_required()
def home(request):
    '''
        GET request.GET['type'] for bulletin type or all if none.
        POST creates a new bulletin
    '''
    bbuser = request.staff
    if bbuser.is_bb_admin:
        messages = Bulletin.objects.all().filter(type="message").exclude(tag='Promotions')
        personal = Bulletin.objects.all().filter(type="personal")
    else:
        personal = Bulletin.objects.all().filter(Q(toStores=bbuser.store)|Q(toGroups__stores=bbuser.store), started=True, type="personal").values('pk').distinct()
        personal = Bulletin.objects.all().filter(pk__in=personal)
        [x.markRead(bbuser.store) for x in personal]
        messages = Bulletin.objects.all().filter(Q(toStores=bbuser.store)|Q(toGroups__stores=bbuser.store), Q(started=True)|Q(archived=True), type="message").values('pk').distinct()
        messages = Bulletin.objects.all().filter(pk__in=messages).exclude(tag='Promotions')
    context = {
        "bbuser": bbuser,
        "messages": messages,
        "personal": personal
    }
    return render(request, 'bulletins/list.html', context)

@login_required()
def collations(request):
    '''
        GET request.GET['type'] for bulletin type or all if none.
        POST creates a new bulletin
    '''
    bbuser = request.staff
    if bbuser.is_bb_admin:
        long = Bulletin.objects.all().filter(type="long")
        short = Bulletin.objects.all().filter(type="short")
        collationOrders = CollationOrder.objects.all().filter(totalQuantity__gt=0)
    else:
        short = Bulletin.objects.all().filter(Q(toStores=bbuser.store)|Q(toGroups__stores=bbuser.store), Q(started=True)|Q(archived=True), type="short").values('pk').distinct()
        short = Bulletin.objects.all().filter(pk__in=short)
        long = Bulletin.objects.all().filter(Q(toStores=bbuser.store)|Q(toGroups__stores=bbuser.store), Q(started=True)|Q(archived=True), type="long").values('pk').distinct()
        long = Bulletin.objects.all().filter(pk__in=long)
        collationOrders = CollationOrder.objects.all().filter(store=bbuser.store, totalQuantity__gt=0).extra(select={'is_open': "status == 'Open'"})
        collationOrders = collationOrders.extra(order_by=['-is_open', '-created'])
    context = {
        "bbuser": bbuser,
        "long": long,
        "short": short,
        "collationOrders": collationOrders,
    }
    return render(request, 'collations/list.html', context)

@login_required()
def collation(request, pk):
    bbuser = request.staff
    collation = get_object_or_404(Collation, pk=pk)
    orders = CollationOrder.objects.filter(collation=collation, totalQuantity__gt=0)
    declined = CollationResponse.objects.all().filter(collation=collation, yes=False)
    context = {
        'collation': collation,
        'orders': orders,
        'bbuser': bbuser,
        'declined': declined,
    }
    return render(request, 'collations/view.html', context)

@login_required()
def downloadCollation(request, pk):
    collation = get_object_or_404(Collation, pk=pk)
    orders = CollationOrder.objects.filter(collation=collation, totalQuantity__gt=0)
    if request.method == "GET" and len(request.GET.get('orders', '')):
        ids = json.loads(request.GET['orders'], encoding="utf-8")
        print ids
        orders = orders.filter(pk__in=ids)
    collationlines = CollationItem.objects.filter(collation=collation, deleted=False).values_list('model', flat=True)
    collationlines = [line.encode('ascii', 'ignore') for line in collationlines]
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;filename=%sOrders.csv' % collation.subject.replace(" ", "")
    writer = csv.writer(response)
    towrite = ['Store Name', 'Delivery Month',]
    towrite.extend(collationlines)
    towrite.append('Order Number')
    if collation.orderMethod == 'EDI':
        towrite.append('HO Order Number')
    towrite.append('Store Comments')
    writer.writerow(towrite)
    for order in orders:
        orderlineQuantitys = CollationOrderLine.objects.filter(order=order, collationLine__deleted=False).values_list('quantity', flat=True)
        towrite = [order.store.name, order.deliveryMonth.month, ]
        towrite.extend(orderlineQuantitys)
        towrite.append(order.orderNumber)
        if collation.orderMethod == 'EDI':
            towrite.append(order.hoOrderNumber)
        towrite.append(order.storeComment)
        writer.writerow(towrite)
    return response

@login_required()
def saveCollation(request, type):
    bbuser = request.staff
    if request.method == 'POST' and len(request.POST['collationData']):
        #save the collation
        collationData = json.loads(request.POST['collationData'], encoding="utf-8")
        collation = collationFromJson(collationData, type, bbuser)
        collation.updateCollation()
        collation.clearRead()
        return HttpResponse(json.dumps({"redirect": reverse('bulletins:collations')}))
    return HttpResponse(json.dumps({"error": "No data sent"}))

@login_required()
def createCollation(request, type):
    bbuser = request.staff
    stores = Store.objects.all()
    groups = Group.objects.all()

    context = {
        "type": type,
        "stores": stores,
        "groups": groups,
        "bbuser": bbuser,
    }
    return render(request, 'collations/create.html', context)

@login_required()
def openCollation(request, pk):
    bbuser = request.staff
    stores = Store.objects.all()
    groups = Group.objects.all()
    collation = get_object_or_404(Collation, pk=pk)
    collationData = json.dumps(jsonFromCollation(collation))

    context = {
        "stores": stores,
        "groups": groups,
        "bbuser": bbuser,
        "collation": collation,
        "type": collation.type,
        "collationData": collationData,
    }
    return render(request, 'collations/update.html', context)

@login_required()
def promotions(request, type):
    bbuser = request.staff
    allPromotions = Promotion.objects.all().filter(promotionType__istartswith=type)
    if not bbuser.is_bb_admin: #stores view.
        promotions = allPromotions.filter(Q(toStores=bbuser.store)|Q(toGroups__stores=bbuser.store)).values('pk').distinct()
        promotions = allPromotions.filter(pk__in=promotions)
        archived = promotions.filter(archived=True, started=False)
        expired_list = promotions.filter(endDate__lt=timezone.now().date(), started=True, archived=False)
        expired = paginate_queryset(expired_list, request.GET.get('expiredPage'))
        pending_list = promotions.filter(started=False, archived=False)
        pending = paginate_queryset(pending_list, request.GET.get('pendingPage'))
        current_list = promotions.filter(endDate__gt=timezone.now().date(), started=True, archived=False)
        current = paginate_queryset(current_list, request.GET.get('currentPage'))
        today = timezone.localtime(timezone.now()).date()
    else: #admin view
        archived_list = allPromotions.filter(archived=True, started=False)
        archived = archived_list
        #archived = paginate_queryset(archived_list, request.GET.get('archivedPage'))
        expired_list = allPromotions.filter(endDate__lt=timezone.now().date(), started=True, archived=False)
        expired = paginate_queryset(expired_list, request.GET.get('expiredPage'))
        pending_list = allPromotions.filter(started=False, archived=False)
        pending = paginate_queryset(pending_list, request.GET.get('pendingPage'))
        current_list = allPromotions.filter(endDate__gt=timezone.now().date(), started=True, archived=False)
        current = paginate_queryset(current_list, request.GET.get('currentPage'))
    context = {
        "bbuser": bbuser,
        "pending": pending,
        "current": current,
        "expired": expired,
        "archived": archived,
    }
    return render(request, 'promotions/list.html', context)

class BulletinCreateView(LoginRequiredMixin, CreateView):
    model = Bulletin
    form_class = BulletinForm
    template_name = 'bulletins/create.html'
    success_url = reverse_lazy('bulletins:home')

    def form_valid(self, form):
        bulletin = form.save(commit=False)
        bbuser = self.request.staff
        bulletin_type = self.kwargs.get('bulletin_type') or self.request.GET.get('bulletin_type') or self.request.POST.get('bulletin_type') or ''
        if bulletin_type == 'short' or bulletin_type == 'long':
            self.success_url = reverse_lazy('bulletins:collations')
        bulletin.origin = bbuser
        bulletin.type = bulletin_type
        bulletin.setArchivedAndStarted()
        bulletin.save()
        form.save_m2m()
        bulletin.notifyStores()
        return HttpResponseRedirect(self.success_url)

class BulletinUpdateView(LoginRequiredMixin, UpdateView):
    model = Bulletin
    form_class = BulletinForm
    template_name = 'bulletins/update.html'
    success_url = reverse_lazy('bulletins:home')

    def form_valid(self, form):
        bulletin = form.save()
        bulletin.setArchivedAndStarted()
        bulletin.save()
        bulletin.clearRead()
        if bulletin.type == 'short' or bulletin.type == 'long':
            self.success_url = reverse_lazy('bulletins:collations')
        return HttpResponseRedirect(self.success_url)

class PromotionCreateView(BulletinCreateView):
    model = Promotion
    form_class = PromotionForm
    success_url = reverse_lazy('bulletins:home')

    def get_context_data(self, **kwargs):
        context = super(PromotionCreateView, self).get_context_data(**kwargs)
        context['isPromotion'] = True
        return context

class PromotionUpdateView(BulletinUpdateView):
    model = Promotion
    form_class = PromotionForm
    success_url = reverse_lazy('bulletins:home')

    def get_context_data(self, **kwargs):
        context = super(PromotionUpdateView, self).get_context_data(**kwargs)
        context['isPromotion'] = True
        return context

@login_required()
def bulletin(request, pk):
    '''
        GET get bulletin for bulletin json (mark as read)
        POST['action'] = DELETE for delete
        POST['action'] = PUT for update
    '''
    bulletin = Bulletin.objects.get(pk=pk)
    bbuser = request.staff
    #mark as read if doesn't exist
    if bbuser.store:
        bulletin.markRead(bbuser.store)
    if request.method == "GET":
        JsonResponse = json.dumps(bulletin.toObj(bbuser.store))
        return HttpResponse(JsonResponse)
    elif request.method =="POST":
        if not bbuser.is_bb_admin:
            raise PermissionDenied
        if request.POST['action'] == 'DELETE':
            bulletin.delete()
            return HttpResponse(json.dumps({"success": True}))
        else:
            return Http404()
    else:
        return Http404()

@login_required()
def collationOrder(request, pk=None, collation_pk=None):
    '''
        GET get bulletin for bulletin json (mark as read)
        POST['action'] = DELETE for delete
        POST['action'] = PUT for update
    '''
    bbuser = request.staff
    store = bbuser.store
    if request.method == "GET":
        if collation_pk:
            collation = Collation.objects.get(pk=collation_pk)
            return render(request, 'collationresponse/multiple.html', {'collation': collation, 'collationOrdersForStore': collation.collationOrdersForStore(store), 'store': store})
        elif pk:
            order = CollationOrder.objects.get(pk=pk)
            return render(request, 'collationresponse/single.html', {'order': order})
    elif request.method =="POST":
        if request.POST['action'] == "CREATE":
            orders = json.loads(request.POST['orders'])
            updateOrders(orders=orders, admin=bbuser.is_bb_admin)
            if collation_pk:
                collation = Collation.objects.get(pk=collation_pk)
                if store:
                    response = CollationResponse.objects.get_or_create(store=store, collation=collation)[0]
                    response.yes = True
                    response.save()
                    #reminder = CollationReminder.objects.get_or_create(store=store, collation=collation)[0]
                    #reminder.delete()
            return HttpResponse(json.dumps({"success": True}))
        elif request.POST['action'] == "DELETE":
            for jsonOrder in json.loads(request.POST['orders']):
                order = CollationOrder.objects.get(pk=jsonOrder['id'])
                try:
                    #delete the responses.
                    response = CollationResponse.objects.get(store=order.store, collation=order.collation)
                    response.delete()
                    #reminder = CollationReminder.objects.get(store=order.store, collation=order.collation)
                    #reminder.delete()
                except CollationResponse.DoesNotExist:#, CollationReminder.DoesNotExist:
                    pass
                order.delete()
            return HttpResponse(json.dumps({"success": True}))
        elif request.POST['action'] == "REJECT":
            #action response => always no : reason => reason why
            collation = Collation.objects.get(pk=collation_pk)
            response = CollationResponse.objects.get_or_create(store=store, collation=collation)[0]
            response.yes = False
            response.reason = request.POST['reason']
            response.save()
            #reminder = CollationReminder.objects.get_or_create(store=store, collation=collation)[0]
            #reminder.delete()
            return HttpResponse(json.dumps({"success": True}))
        elif request.POST['action'] == "LATER":
            #ask me later - create a reminder for x days after
            #collation = Collation.objects.get(pk=collation_pk)
            #reminder = CollationReminder.objects.get_or_create(store=store, collation=collation)[0]
            #reminder.remindOn = timezone.localtime(timezone.now())+timedelta(days=1)
            #reminder.save()
            return HttpResponse(json.dumps({"success": True}))