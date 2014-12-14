from django.forms import ModelForm
from models import CSVUpload


class UploadCSVForm(ModelForm):

    class Meta:
        exclude = ['uploadType', 'saved', 'expiryDate', 'createdBy']
        model = CSVUpload




