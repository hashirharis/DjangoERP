from django.forms import ModelForm

from pos.models import Terminal, Customer, LedgerAccount, PaymentMethod
from core.forms import StoreLevelObjectForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, MultiField, Div, HTML, Fieldset

class CustomerForm(StoreLevelObjectForm):
    class Meta:
        model = Customer
        exclude = ('account',)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'title',
                    'firstName',
                    'lastName',
                    'VCN',
                    'homePhone',
                    'workPhone',
                    'fax',
                    'mobile',
                    'email',
                    'preferredContact',
                    css_class="col-lg-6 col-12",
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
                    css_class="col-lg-6 col-12",
                ),
                css_class="col-12"
            )
        )
        super(CustomerForm, self).__init__(*args, **kwargs)

class PaymentMethodForm(StoreLevelObjectForm):
    class Meta:
        model = PaymentMethod