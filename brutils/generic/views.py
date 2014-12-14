from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from brutils.decorators import access_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, InvalidPage

import json

'''
whenever you want login_required on one of the views add this mixin.
class SomeProtectedViewView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
'''
class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

class LoginAndAdminPrivelege(object):
    @method_decorator(login_required)
    @method_decorator(access_required('admin'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginAndAdminPrivelege, self).dispatch(request, *args, **kwargs)

class LoginAndSalePrivelege(object):
    @method_decorator(login_required)
    @method_decorator(access_required('sale'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginAndSalePrivelege, self).dispatch(request, *args, **kwargs)

class LoginAndStockPrivelege(object):
    @method_decorator(login_required)
    @method_decorator(access_required('stock'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginAndStockPrivelege, self).dispatch(request, *args, **kwargs)

class JSONCreateView(CreateView):
    def form_invalid(self, form):
        errors = {'errors': form.errors}
        return HttpResponse(json.dumps(errors))
    def form_valid(self, form):
        form.save()
        return HttpResponse(json.dumps({'success': True, }))

class StoreLevelObjectMixin(object):
    def get_form_kwargs(self):
        kwargs = super(StoreLevelObjectMixin, self).get_form_kwargs()
        kwargs['store'] = self.request.store
        return kwargs

    def storeLevelFormSanitize(self, form):
        formobject = form.save(commit=False)
        store = self.request.store
        if store.isHead and formobject.isShared:
            formobject.isShared = True
        else:
            formobject.isShared = False
        formobject.store = store
        formobject.group = store.group
        return formobject

class JSONFormView(FormView):
    def form_invalid(self, form):
        errors = {'errors': form.errors}
        return HttpResponse(json.dumps(errors))
    def form_valid(self, form):
        form.save()
        return HttpResponse(json.dumps({'success': True, }))

class JSONUpdateView(UpdateView):
    def form_invalid(self, form):
        errors = {'errors': form.errors}
        return HttpResponse(json.dumps(errors))
    def form_valid(self, form):
        form.save()
        return HttpResponse(json.dumps({'success': True, }))

class JSONDeleteView(DeleteView):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse(json.dumps({'success': True, }))

class BRListView(ListView):
    context_append = {}

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, if needed.
        """
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or self.request.POST.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_("Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
                                'page_number': page_number,
                                'message': str(e)
            })

    def get_context_data(self, **kwargs):
        context = super(BRListView, self).get_context_data(**kwargs)
        context.update(self.context_append)
        return context

    def post(self, request, *args, **kwargs):
        return super(BRListView, self).get(request, *args, **kwargs)