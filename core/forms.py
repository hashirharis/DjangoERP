from django import forms
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div

from core.models import *
from datetime import datetime

class StoreLevelObjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.store = kwargs['store']
        del kwargs['store']
        super(StoreLevelObjectForm, self).__init__(*args, **kwargs)
        if not self.store.isHead:
            del self.fields['isShared']
        del self.fields['store']
        del self.fields['group']

class ProductForm(StoreLevelObjectForm):
    class Meta:
        model = Product
        exclude = ['costPrice', 'spanNet']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'model',
                    'description',
                    'category',
                    'brand',
                    'EAN',
                    'packSize',
                    'tradePrice',
                    'goPrice',
                    css_class="col-12 col-lg-6",
                ),
                Div(
                    'isCore',
                    'isGSTExempt',
                    'isShared',
                    'status',
                    'tags',
                    'manWarranty',
                    css_class="col-12 col-lg-6",
                ),
                css_class="col-12"
            )
        )
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = [[category.id, category.name] for category in ProductCategory.objects.all().filterReadAll(self.store).exclude(parentCategory__name__istartswith='Extended')]
        self.fields['brand'].choices = [[brand.id, brand.brand] for brand in Brand.objects.all().filterReadAll(self.store)]
        self.fields['tags'].choices = [[tag.id, tag.tag] for tag in ProductTag.objects.all().filterReadAll(self.store).filter(Q(type__exact='Feature') | Q(type__exact='Other'))]

class WarrantyForm(ProductForm):
    class Meta:
        model = Warranty
        exclude = ['costPrice', 'spanNet', 'EAN', 'packSize']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'model',
                    'description',
                    'category',
                    'brand',
                    'tradePrice',
                    'goPrice',
                    css_class="col-12 col-lg-6",
                ),
                Div(
                    'isCore',
                    'isGSTExempt',
                    'isShared',
                    'status',
                    'tags',
                    'startValue',
                    'endValue',
                    css_class="col-12 col-lg-6",
                ),
                css_class="col-12"
            )
        )
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = [[category.id, category.name] for category in ProductCategory.objects.all().filterReadAll(self.store).filter(depth=2, parentCategory__name__istartswith='Extended')]
        self.fields['brand'].choices = [[brand.id, brand.brand] for brand in Brand.objects.all().filterReadAll(self.store)]
        self.fields['tags'].choices = [[tag.id, tag.tag] for tag in ProductTag.objects.all().filterReadAll(self.store).filter(Q(type__exact='Feature') | Q(type__exact='Other'))]

class TagForm(StoreLevelObjectForm):
    class Meta:
        model = ProductTag

    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = [['Feature', 'Feature'], ['Other', 'Other']]

class ProductCategoryForm(StoreLevelObjectForm):
    class Meta:
        model = ProductCategory
        exclude = ('depth',)

    def __init__(self, *args, **kwargs):
        super(ProductCategoryForm, self).__init__(*args, **kwargs)
        self.fields['extWarrantyTypes'].choices = [[category.id, category.name] for category in ProductCategory.objects.all().filterReadAll(self.store).filter(depth=2, parentCategory__name__istartswith='Extended')]

class ProductCategoryMarkupForm(forms.ModelForm):
    class Meta:
        model = ProductCategoryMarkup
        exclude = ('store', 'category')

class BrandForm(StoreLevelObjectForm):
    class Meta:
        model = Brand

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        'hasElectronicTrading',
                        css_class="span2"
                    ),
                    Div(
                        'isHOPreferred',
                        css_class="span2"
                    ),
                    Div(
                        'isInGFK',
                        css_class="span2"
                    ),
                    Div(
                        css_class="clearfix"
                    ),
                    'brand',
                    'purchaser',
                    'distributor',
                    'repName',
                    'repPhone',
                    'ABN',
                    'GLN',
                    'rebate',
                    'actualRebate',
                    css_class="col-6",
                ),
                Div(
                    Div(
                        'address',
                        'suburb',
                        'cityState',
                        'postcode',
                        style = 'background:#DFF0D8;',
                    ),
                    Div(
                        'paddress',
                        'psuburb',
                        'pcityState',
                        'ppostcode',
                        style = 'background:#EEE;'
                    ),
                    css_class="col-6",
                ),
                'comments',
                css_class="col-12"
            )
        )
        super(BrandForm, self).__init__(*args, **kwargs)
        if not self.store.code == "HO":
            del self.fields['actualRebate']

class DealForm(forms.ModelForm):
    startDate = forms.DateTimeField(input_formats=['%m/%d/%Y'], widget=forms.DateTimeInput(format="%m/%d/%Y"))
    endDate = forms.DateTimeField(input_formats=['%m/%d/%Y'], widget=forms.DateTimeInput(format="%m/%d/%Y"))

    def __init__(self, *args, **kwargs):
        deal = kwargs.get('instance')
        super(DealForm, self).__init__(*args, **kwargs)
        if deal and deal.id:
            del self.fields['type']
            if deal.type != 'ST':
                del self.fields['claimFrom']

    class Meta:
        model = Deal
        exclude = ('active', 'createdBy', 'createdOn', 'product')

    def save(self, commit=True, force_insert=False, force_update=False, *args, **kwargs):
        m = super(forms.ModelForm, self).save(commit=False, *args, **kwargs)
        #activation logic
        now = datetime.now()
        startDate = datetime(m.startDate.year, m.startDate.month, m.startDate.day)
        endDate = datetime(m.endDate.year, m.endDate.month, m.endDate.day)
        today = datetime(now.year, now.month, now.day)
        if startDate <= today:
            m.active = True
            if endDate <= today:
                m.active = False
        else:
            m.active = False
        return m

    def clean_startDate(self):
        startDate = self.cleaned_data['startDate']
        endDate = self.cleaned_data.get('endDate',None)
        if endDate is not None:
            if endDate < startDate:
                raise forms.ValidationError("End Date Cannot Be Before Start Date!")

        return startDate

    def clean_endDate(self):
        endDate = self.cleaned_data['endDate']
        compareThis = datetime(endDate.year,endDate.month,endDate.day)
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        if compareThis < today:
            raise forms.ValidationError("End Date Cannot Be Before Today!")
        return endDate

    def clean(self):
        cleaned_data = super(forms.ModelForm, self).clean()
        startDate = cleaned_data.get("startDate")
        endDate = cleaned_data.get("endDate")

        if startDate and endDate:
            # Only do something if both fields are valid so far.
            if startDate > endDate:
                msg = u"End date must be after start date"
                self._errors["endDate"] = self.error_class([msg])
                self._errors["startDate"] = self.error_class([msg])
                del cleaned_data["startDate"]
                del cleaned_data["endDate"]

        # Always return the full collection of cleaned data.
        return cleaned_data

class VendorBonusForm(DealForm):
    class Meta:
        model = ClassVendorBonus
        exclude = ('active', 'createdBy', 'createdOn', 'brand')

    def __init__(self, *args, **kwargs):
        self.store = kwargs['store']
        del kwargs['store']
        deal = kwargs.get('instance')
        super(DealForm, self).__init__(*args, **kwargs)
        self.fields['startDate'].label = "Start Date"
        self.fields['endDate'].label = "End Date"
        if deal and deal.id:
            del self.fields['type']
        else:
            self.fields['type'].choices = [[category.id, category.name] for category in ProductCategory.objects.all().filterReadAll(self.store)]

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount > 100:
            raise forms.ValidationError("This is meant to be a percent! You will be discounting the entire product")
        return amount

