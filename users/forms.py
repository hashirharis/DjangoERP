from django import forms
from users.models import Staff, StoreProfile, Store

class StaffForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirmPassword = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = Staff
        exclude = ('store', )
        fields = ('name', 'username', 'password', 'confirmPassword', 'initials', 'privelegeLevel')

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        if self.instance.id is not None:
            del self.fields['confirmPassword']
            del self.fields['password']

    def clean(self):
        cleaned_data = super(StaffForm, self).clean()
        #make sure the initials are unique to this store.
        username = cleaned_data.get("username")
        store = self.instance.store
        if Staff.objects.filter(username=username, store=store).exclude(pk=self.instance.id).count():
            msg = u"There is another user with this username"
            self._errors["username"] = self.error_class([msg])
            del cleaned_data["username"]
        #make sure the passwords match if creating
        if self.instance.id is None:
            password = cleaned_data.get("password")
            confirmPassword = cleaned_data.get("confirmPassword")
            if password != confirmPassword:
                msg = u"Passwords do not match!"
                self._errors["confirmPassword"] = self.error_class([msg])
        return cleaned_data

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        exclude = ('group', 'isHead', 'user', 'spanStoreID', 'code', 'name', 'openToBuy', 'purchaseLimit', 'extendedCreditTotals', 'currentDebt', 'irpInvoices', 'notInvoiced', 'openToBuy', )

class FinancialsForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ('purchaseLimit', 'currentDebt')

class SalesSettingsForm(forms.ModelForm):
    class Meta:
        model = StoreProfile
        fields = (
            'noStockWarning', 'warrantyOffer', 'useGoPrice', 'useCatalogPrice', 'salePriceWarnings', 'customerNotAttached',
            'paymentDetailsOnInvoice', 'printDeliveryDetails',
            'showSellThrough', 'floatValue', 'quotationsExpiry'
        )

class PrivelegeLevelsForm(forms.ModelForm):
    class Meta:
        model = StoreProfile
        fields = ('reportsLevel', 'creditLimits')

class ResetPasswordForm(forms.Form):
    newPassword = forms.CharField(widget=forms.PasswordInput(), label="New Password")
    confirmNewPassword = forms.CharField(widget=forms.PasswordInput(), label="Confirm New Password")

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        password = cleaned_data.get("newPassword")
        confirmPassword = cleaned_data.get("confirmNewPassword")
        if password != confirmPassword:
            msg = u"Passwords do not match!"
            self._errors["confirmNewPassword"] = self.error_class([msg])
        return cleaned_data