from django import forms

from dnow.models import Profile


class SettingForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('googleSpreadSheet', 'googleDriveEmail', 'church')
