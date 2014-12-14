from django import forms
from django.db.models import Q

from stock.models import ManualStockMovement

class ManualStockMovementForm(forms.ModelForm):
    type_choices = (
        ('IN', 'Book In'),
        ('OUT', 'Book Out'),
    )
    product = forms.IntegerField(min_value=1)
    type = forms.ChoiceField(choices=type_choices)
    quantity = forms.IntegerField(min_value=1)
    purchaseNet = forms.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        model = ManualStockMovement
        exclude = ('createdBy', )
        fields = (
            'type',
            'product',
            'quantity',
            'purchaseNet',
            'comments'
        )