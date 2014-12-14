from b2b.models import StorePayment
from django import forms

class StorePaymentForm(forms.ModelForm):

    class Meta:
        model = StorePayment
        exclude = ('store',)
