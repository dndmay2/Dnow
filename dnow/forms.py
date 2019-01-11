from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from encrypted_model_fields.fields import EncryptedCharField

from dnow.models import Profile, EmailTemplate, HostHome, Driver, Leader, Student


class SettingForm(forms.ModelForm):
    # churchEmailPassword = forms.CharField(widget=forms.PasswordInput)
    churchEmailPassword = EncryptedCharField()

    class Meta:
        model = Profile
        fields = ('googleSpreadSheet', 'churchEmailAddress', 'churchName', 'churchEmailPassword')

    def __init__(self, *args, **kwargs):
        super(SettingForm, self).__init__(*args, **kwargs)
        self.fields['churchEmailPassword'].widget = forms.PasswordInput()

# class EmailForm(forms.ModelForm):
#
#     class Meta:
#         model = Email
#         fields =

class EmailTemplateForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Email Template Name',
                'size': '50'
            }
        )
    )
    greeting = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Enter text to appear at top of email',
                'rows': 4
            }
        )
    )
    closing = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Enter text to appear at bottom of email',
                'rows': 4
            }
        )
    )
    toGroups = forms.ChoiceField(
        label = "To groups",
        choices = EmailTemplate.TO_GROUPS,
        widget = forms.RadioSelect
    )
    includeData = forms.MultipleChoiceField(
        label = "Include sections",
        choices = EmailTemplate.EMAIL_DATA,
        widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = EmailTemplate
        fields = ('name', 'greeting', 'closing', 'toGroups', 'includeData')

    def __init__(self, *args, **kwargs):
        super(EmailTemplateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # self.helper.add_input(Submit('submit', 'Save Template'))
        self.helper.layout = Layout(
            'name',
            'greeting',
            'closing',
            Row(
                Column('toGroups', css_class='form-group col-md-6 mb-0'),
                Column('includeData', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            # 'toGroups',
            # 'includeData',
            Submit('submit', 'Save Template')
        )


class HostHomeDropDownForm(forms.Form):
    hostHomes = forms.ModelChoiceField(queryset=HostHome.objects.all().order_by('lastName'),
                                       widget=forms.Select(attrs={"onChange": 'submit()'}),
                                       empty_label="All",
                                       required=False)

    def __init__(self, user, *args, **kwargs):
        super(HostHomeDropDownForm, self).__init__(*args, **kwargs)
        # Keep only host homes with students (__isnull requires distinct)
        self.fields['hostHomes'].queryset = HostHome.objects.filter(
            user=user, student__isnull=False).distinct().order_by('lastName')

# class HostHomeDropDownForm(forms.Form):
#     hostHomes = forms.ModelChoiceField(queryset=HostHome.objects.all().order_by('lastName'),
#                                        # widget=forms.Select(attrs={'onchange': 'HostHomeDropDownForm.submit();'}),
#                                        empty_label="(All)")
#     drivers = forms.ModelChoiceField(queryset=Driver.objects.all().order_by('lastName'))
#     leaders = forms.ModelChoiceField(queryset=Leader.objects.all().order_by('lastName'))
#     students = forms.ModelChoiceField(queryset=Student.objects.all().order_by('lastName'))
#
#     def __init__(self, user, *args, **kwargs):
#         super(HostHomeDropDownForm, self).__init__(*args, **kwargs)
#         self.fields['hostHomes'].queryset = HostHome.objects.filter(user=user).order_by('lastName')
#         self.fields['drivers'].queryset = Driver.objects.filter(user=user).order_by('lastName')
#         self.fields['leaders'].queryset = Leader.objects.filter(user=user).order_by('lastName')
#         self.fields['students'].queryset = Student.objects.filter(user=user).order_by('lastName')

