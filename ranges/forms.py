# !/usr/bin/env python

from django import forms
from users import models as usermodel
from core.models import Product
from django.forms.extras import SelectDateWidget
import models
from django.core.exceptions import ValidationError



STORE_CHOICES = (
    ('G', 'Gold'),
    ('S', 'Silver'),
    ('B', 'Bronze'),
)
CHOICES = (('1', 'Yes',), ('0', 'No',))


class NumberInput(forms.TextInput):
    input_type = 'number'
    type = 'number'
    attrs = {'disabled': 'disabled'}


class DateInputCustom(forms.DateInput):
    input_type = 'text'
    type = 'text'
    attrs = {'disabled': 'disabled'}


class AddStoreForm(forms.Form):
    storeName = forms.ChoiceField(label=u'Store Name', required=True)
    storeName.widget.attrs.update({'class': 'form-control select2-container'})
    rangeType = forms.ChoiceField(widget=forms.Select(), choices=STORE_CHOICES, required=True , label="Range Type")
    rangeType.widget.attrs.update({'class': 'form-control select2-container uneditable-input'})
    month = forms.CharField(max_length=20,required=True)
    month.widget.attrs.update({'class': 'form-control monthpicker','required':'true'})

    def __init__(self, *args, **kwargs):
        super(AddStoreForm, self).__init__(*args, **kwargs)
        self.fields['storeName'].choices = [(e.id, e.name) for e in usermodel.Store.objects.all().order_by('name')]


class UpdateProductRangeForm(forms.ModelForm):
    bonus = forms.CharField(widget=forms.TextInput(attrs={'required': "true","type": "number",
                                                          'class': 'monthpicker mtz-monthpicker-widgetcontainer form-control select2-container'}), label='$Bonus')
    class Meta:
        model = models.ProductRange
        exclude = ('product', 'productRange')
        widgets = {
            'guaranteed': forms.CheckboxInput(attrs={"class": 'form-control'}),
            'bonus': forms.TextInput(attrs={'required': "true","type": "number",'class': 'monthpicker mtz-monthpicker-widgetcontainer form-control select2-container'}),
            'month': forms.TextInput(attrs={'class': 'monthpicker mtz-monthpicker-widgetcontainer form-control select2-container',
                                            'id': 'monthpicker', 'required':"true"}),
        }


class UpdateRangeForm(forms.ModelForm):
    rangeType = forms.ChoiceField(widget=forms.Select(attrs={"class": 'form-control'}), choices=STORE_CHOICES, required=True , label="Range Type")
    def clean_month(self):
        month = self.cleaned_data['month']
        return month

    class Meta:
        model = models.StoreRange
        exclude = ('store', 'month')
        widgets = {
            'month': forms.TextInput(attrs={'class': 'monthpicker mtz-monthpicker-widgetcontainer uneditable-input',
                                            'id': 'monthpicker', }),
        }


class UpdateRange_cleaned(UpdateRangeForm):
    def clean_month(self):
        data = self.cleaned_data['month']





class AddProductForm(forms.Form):
    product = forms.ChoiceField(label="Product", required=True)
    product.widget.attrs.update({'class': 'col-4 form-control select2-container'})
    month = forms.CharField(required=True, max_length=20, widget=DateInputCustom(
        attrs={"class": 'monthpicker form-control uneditable-input', 'id': 'productmonthpicker', 'required': 'true'}))
    guaranteed = forms.BooleanField(label=u'Guaranteed', widget=forms.CheckboxInput, initial=False, required=False)
    guaranteed.widget.attrs.update({'class': 'select2-container'})
    rangeType_gold = forms.BooleanField(required=False,label='gold', widget=forms.CheckboxInput(attrs={'': ''}))
    rangeType_silver = forms.BooleanField(required=False,label='silver', widget=forms.CheckboxInput(attrs={'': ''}))
    rangeType_bronz = forms.BooleanField(required=False,label='bronze', widget=forms.CheckboxInput(attrs={'': ''}))
    gold_bonus = forms.IntegerField(required=False,widget=NumberInput(attrs={'class': 'form-control','required':'true'}))
    silver_bonus = forms.IntegerField(required=False,widget=NumberInput(attrs={'class': 'form-control','required':'true'}))
    bronze_bonus = forms.IntegerField(required=False,widget=NumberInput(attrs={'class': 'form-control','required':'true'}))

    def clean_month(self):
        month = self.cleaned_data['month']
        print len(month.split('/'))
        if len(month.split('/')) >= 2:
            if (month.split('/')[0]).isdigit():
                if (month.split('/')[1]).isdigit():
                    return self.cleaned_data['month']
                else:
                    return forms.ValidationError("invalid year")
            else:
                return forms.ValidationError("invalid month")
        else:
            return forms.ValidationError("invalid month format ( should be in format of mm/yyyy)")


    def __init__(self, *args, **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)
        self.fields['product'].choices = [(e.id, e.model) for e in Product.objects.all().order_by('model')]

