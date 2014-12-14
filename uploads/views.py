import os
import dynamicCSV
first_page = 0
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView
from forms import UploadCSVForm
from django.core.urlresolvers import reverse
from uploads.models import CSVUpload
from django.template import RequestContext
from django.shortcuts import render_to_response
from dynamicCSV import writeToDB
from brutils.generic.views import *
from users.models import Staff
from django.shortcuts import get_object_or_404


class HomeView(LoginRequiredMixin, FormView):
    template_name = 'uploads-home.html'
    success_url = reverse_lazy('uploads:home')
    form_class = UploadCSVForm

    def form_valid(self, form):
        self.request.session['modelslist'] = []
        form.save(commit=False)
        global first_page
        first_page = 1
        uploadType = os.path.basename(form.instance.csvFile.path).split('_')[0]
        uploadType = uploadType.split(' ')[0]
        if uploadType.lower() in ['catalogue', 'products', 'writeups']:
            form.instance.uploadType = uploadType
            staff = get_object_or_404(Staff, pk=self.request.staff.id)
            form.instance.createdBy = staff
            form.save()
            dynamicCSV.setUploadExpiry(form.instance.id, uploadType)
            return HttpResponseRedirect(reverse('uploads:home', kwargs={'pk': form.instance.id}))
        else:
            return HttpResponseRedirect(reverse('uploads:home', kwargs={'pk': 0}))

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data()
        global first_page
        pk = self.kwargs.get('pk')
        dynamicCSV.addContextForViewAllWidget(self, context)
        context['first_page'] = first_page
        first_page = 0
        passedValidation = True
        uploadType = dynamicCSV.getTypeFromUpload(pk)
        if pk is None or pk == '0':  #  load initial home page or fileNameSyntaxError
            if pk == '0':
                context['fileNameSyntaxError'] = True
            context['hasPK'] = False
            context['pk'] = 0  # dummy value for initial homepage load
            pk = 0             # dummy value for initial homepage load
        else:  # validate data
            rowsFromUpload = dynamicCSV.getRowsFromUpload(pk)
            firstRowFromUpload = dynamicCSV.getFirstRowFromUpload(pk)
            if uploadType == 'products':
                passedValidation = dynamicCSV.validateProducts(pk, uploadType, rowsFromUpload, firstRowFromUpload, context)
            elif uploadType == 'catalogue':
                passedValidation = dynamicCSV.validateCatalogue(pk, uploadType, rowsFromUpload, firstRowFromUpload, context)
                WriteOrDeleteUploadIfInvalid(self.request, pk, passedValidation)
            elif uploadType == 'writeups':
                passedValidation = dynamicCSV.validateWriteup(pk, uploadType, rowsFromUpload, firstRowFromUpload, context)
                WriteOrDeleteUploadIfInvalid(self.request, pk, passedValidation)
            else:
                dynamicCSV.addContext(pk, uploadType, rowsFromUpload, firstRowFromUpload, context)
                context['pk'] = pk
        if self.request.session.get('modelslist'):
            context['modelslist'] = self.request.session.get('modelslist')
        return context


def WriteOrDeleteUploadIfInvalid(request, pk, passedValidation):
    rowsFromUpload = dynamicCSV.getRowsFromUpload(pk)
    firstRowFromUpload = dynamicCSV.getFirstRowFromUpload(pk)
    listPendingSuperseding = []
    doNotSupersedeList = request.session.get('modelslist')
    context = {}
    context['pk'] = pk
    uploadType = dynamicCSV.getTypeFromUpload(pk)
    if passedValidation:  # display results and writes to DB
        if not pk == 0:
            if uploadType == 'products':
                listPendingSuperseding = dynamicCSV.addWriteContext(pk, context, rowsFromUpload, firstRowFromUpload)
        writeToDB(request.store, pk, context, doNotSupersedeList, uploadType, listPendingSuperseding, rowsFromUpload, firstRowFromUpload)
        #  this is commented out for now
        # dynamicCSV.sendConfirmationEmail(uploadType)
    else:  # show error msg
        CSVUploadObj = CSVUpload.objects.get(id=pk)
        CSVUploadObj.delete()
        context['CSVUploadDoesNotExist'] = True
        context['rowsFromUpload'] = dynamicCSV.getNonExistentProducts(rowsFromUpload, uploadType)
    rc = RequestContext(request)
    return render_to_response('uploads-home.html', context, rc)


def addToSession(request, model, pk=None):
    if not request.session.get('modelslist'):
        request.session['modelslist'] = [model]
    else:
        if not model in request.session['modelslist']:
            updated_list = request.session['modelslist']
            updated_list.append(model)
            request.session['modelslist'] = updated_list[:]
    return HttpResponseRedirect(reverse('uploads:home', kwargs={'pk': pk}))


def removeFromSession(request, model, pk):
    if not request.session.get('modelslist'):
        request.session['modelslist'] = [model]
    else:
        if model in request.session['modelslist']:
            updated_list = request.session['modelslist']
            updated_list.remove(model)
            request.session['modelslist'] = updated_list[:]
    return HttpResponseRedirect(reverse('uploads:home', kwargs={'pk': pk}))

