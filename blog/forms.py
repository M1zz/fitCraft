from django import forms
 
class RegistrationForm(forms.Form):
    username = forms.CharField(label='사용자 이름', max_length=30)
    email = forms.EmailField(label='이메일')
    password1 = forms.CharField(label='비밀번호', widget=forms.PasswordInput())
    password2 = forms.CharField(label='비밀번호 확인', widget=forms.PasswordInput())
