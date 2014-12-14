from django import forms
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from tele.models import AddressbookContact, BrandAddressbookContact

class StoreLevelObjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.store = kwargs['store']
        del kwargs['store']
        super(StoreLevelObjectForm, self).__init__(*args, **kwargs)
        if not self.store.isHead:
            del self.fields['isShared']
        del self.fields['store']
        del self.fields['group']

class ContactForm(StoreLevelObjectForm):
    class Meta:
        model = AddressbookContact

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'name',
                    'address',
                    'landline',
                    'mobile',
                    'email',
                    'fax',
                    'comment',
                    'serviceType',
                    css_class="col-12 col-lg-6",
                ),

                css_class="col-12"
            )
        )
        super(ContactForm, self).__init__(*args, **kwargs)

class LocalBrandRepForm(StoreLevelObjectForm):
    class Meta:
        model = BrandAddressbookContact
        exclude = ('brand', )


    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'repName',
                    'repPhone',
                    'repFax',
                    'repEmail',
                    'localServiceAgent',
                    'comments',
                    css_class="col-12",
                ),

                css_class="col-12"
            )
        )
        super(LocalBrandRepForm, self).__init__(*args, **kwargs)



class BrandContactForm(StoreLevelObjectForm):
    class Meta:
        model = BrandAddressbookContact
        exclude = ('brand', 'serviceType')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'name',
                    'address',
                    'landline',
                    'mobile',
                    'email',
                    'fax',
                    'comment',
                    'serviceType',
                    css_class="col-12 col-lg-6",
                ),

                css_class="col-12"
            )
        )
        super(BrandContactForm, self).__init__(*args, **kwargs)

