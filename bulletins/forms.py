from django import forms
from bulletins.models import Bulletin, Promotion, Store

from crispy_forms.layout import Layout, MultiField, Div, HTML, Fieldset
from crispy_forms.helper import FormHelper

class BulletinForm(forms.ModelForm):
    startDate = forms.DateTimeField(widget=forms.DateTimeInput(format="%m/%d/%Y", attrs={'placeholder': 'Start Date'}), label="Dates")
    endDate = forms.DateTimeField(widget=forms.DateTimeInput(format="%m/%d/%Y",  attrs={'placeholder': 'End Date'}), label="")
    archiveDate = forms.DateTimeField(widget=forms.DateTimeInput(format="%m/%d/%Y", attrs={'placeholder': 'Archive Date'}), label="")

    class Meta:
        model = Bulletin
        exclude = ('origin', 'started', 'archived', 'type', 'modified')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    'subject',
                    css_class="col-12",
                ),
                Div(
                    Div(
                        'startDate',
                        css_class="col-lg-4 col-12 fixedLeft",
                    ),
                    Div(
                        'endDate',
                        css_class="col-lg-4 col-12 fixedLeft",
                    ),
                    Div(
                        'archiveDate',
                        css_class="col-lg-4 col-12 fixedLeft",
                    ),
                    css_class="row"
                ),
                Div(
                    Div(
                        'tag',
                        css_class="col-lg-4 col-12 fixedLeft",
                    ),
                    Div(
                        'toGroups',
                        css_class="col-lg-4 col-12 fixedLeft",
                    ),
                    Div(
                        'toStores',
                        css_class="col-lg-4 col-12 fixedLeft",
                    ),
                    css_class="row",
                ),
                Div(
                    Div(
                        'sendSMS',
                        css_class="col-lg-4 col-12 fixedLeft"
                    ),
                    Div(
                        'sendEmail',
                        css_class="col-lg-4 col-12 fixedLeft"
                    ),
                    css_class="row",
                ),
                Div(
                    Div(
                        'sendSMSReminder',
                        css_class="col-lg-4 col-12 fixedLeft"
                    ),
                    Div(
                        'sendEmailReminder',
                        css_class="col-lg-4 col-12 fixedLeft"
                    ),
                    css_class="row",
                ),
                Div(
                    'content',
                    css_class="col-12",
                ),
                css_class="col-12"
            )
        )
        super(BulletinForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(forms.ModelForm, self).clean()
        startDate = cleaned_data.get("startDate")
        endDate = cleaned_data.get("endDate")
        archiveDate = cleaned_data.get("archiveDate")

        if startDate and endDate and archiveDate:
            # Only do something if all fields are valid so far.
            if startDate > endDate:
                msg = u"End date must be after start date"
                self._errors["endDate"] = self.error_class([msg])
                self._errors["startDate"] = self.error_class([msg])
                del cleaned_data["startDate"]
                del cleaned_data["endDate"]
            elif startDate > archiveDate:
                msg = u"Archive date must be after start date"
                self._errors["archiveDate"] = self.error_class([msg])
                self._errors["startDate"] = self.error_class([msg])
                del cleaned_data["startDate"]
                del cleaned_data["archiveDate"]
        # Always return the full collection of cleaned data.
        return cleaned_data


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store

    def __init__(self, *args, **kwargs):
        super(StoreForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            del self.fields['state']

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

class PromotionForm(BulletinForm):
    class Meta:
        model = Promotion
        exclude = ('origin', 'started', 'archived', 'type')

    def __init__(self, *args, **kwargs):
        super(PromotionForm, self).__init__(*args, **kwargs)
        self.helper.layout[0][4][0].append(Div('eligibleModels'))
        self.helper.layout[0][4][0].append(Div('promotionType'))
        del self.helper.layout[0][2][0]
        self.helper.layout[0][2].append(Div('tag', css_class="col-lg-4 col-12 fixedLeft"))
        self.fields['toGroups'].label = "to Groups"

    def clean(self):
        if self.instance.archived:
            cleaned_data = super(PromotionForm, self).clean()
        else:
            cleaned_data = super(forms.ModelForm, self).clean()
        return cleaned_data