from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from . import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class LoginForm(forms.Form):
    username = forms.CharField(label='姓名', max_length=10)
    password = forms.CharField(label='密碼', widget=forms.PasswordInput())
    username.widget.attrs.update({'class':'form-control'})
    password.widget.attrs.update({'class':'form-control'})
    
class ProfileForm(forms.ModelForm):
    floor = forms.IntegerField(
        label='樓層',
        validators=[MinValueValidator(2), MaxValueValidator(15)],
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    class Meta:
        model = models.Profile
        fields = ['build','floor','household','phone']
        
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['build'].label = '棟數'
        #self.fields['floor'].label = '樓層'
        self.fields['household'].label = '戶別'
        self.fields['phone'].label = '電話'
        self.fields['build'].widget.attrs.update({'class':'form-control'})
        #self.fields['floor'].widget.attrs.update({'class':'form-control'})
        self.fields['household'].widget.attrs.update({'class':'form-control'})
        self.fields['phone'].widget.attrs.update({'class':'form-control'})
        
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label=_('用戶名'), max_length=150)
    password1 = forms.CharField(label=_('密碼'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('確認密碼'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = '姓名'
        self.fields['password1'].label = '密碼'
        self.fields['password2'].label = '確認密碼'
        self.fields['username'].widget.attrs.update({'class':'form-control'})
        self.fields['password1'].widget.attrs.update({'class':'form-control'})
        self.fields['password2'].widget.attrs.update({'class':'form-control'})
        
class DatetimeInput(forms.DateTimeInput):
    input_type='datetime'
    
class ForumForm(forms.ModelForm):
    class Meta:
        model = models.Forum
        fields = ['title', 'body', 'posttime']
        widgets = {
            'posttime':DatetimeInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super(ForumForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = '標題'
        self.fields['title'].widget.attrs.update({'class':'form-control'})
        self.fields['body'].label = '內容'
        self.fields['body'].widget.attrs.update({'class':'form-control'})
        self.fields['posttime'].label = '發布日期'
        self.fields['posttime'].widget.attrs.update({'class':'form-control'})

class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['body']
        widgets = {
            'body': forms.TextInput(attrs={'class':'form-control', 'placeholder':'輸入您的留言...'})
        }
        
class PaymentForm(forms.ModelForm):
    class Meta:
        model = models.ManagementFee
        fields = ['payway']
        
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['payway'].label = '繳費方式'
        self.fields['payway'].widget.attrs.update({'class':'form-control'})
        
class ActivityApplicationForm(forms.ModelForm):
    class Meta:
        model = models.ActivityApplication
        fields = ['participant_count']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ActivityApplicationForm, self).__init__(*args, **kwargs)
        self.fields['participant_count'].widget.attrs.update({'class':'form-control'})
        if user:
            self.fields['user'].initial = user
            self.fields['profile'].initial = user.profile
            self.fields['user'].widget.attrs['readonly'] = True
            self.fields['profile'].widget.attrs['readonly'] = True
    
    def clean_participant_count(self):
        participant_count = self.cleaned_data.get('participant_count')
        if participant_count <= 0:
            raise forms.ValidationError("報名人數至少1人")
        return participant_count