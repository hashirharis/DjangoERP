from django import forms
from django.db.models import Q
from stock.forms import *
from stock.models import ManualStockMovement


class VWManualStockMovementForm(forms.ModelForm):
    type_choices = (
        ('IN', 'Book In'),
        ('OUT', 'Book Out'),
    )
    product = forms.IntegerField(min_value=1)
    type = forms.ChoiceField(choices=type_choices)
    quantity = forms.IntegerField(min_value=1)

    class Meta:
        model = ManualStockMovement
        exclude = ('createdBy', 'purchaseNet')
        fields = (
            'type',
            'product',
            'quantity',
            'comments'
        )