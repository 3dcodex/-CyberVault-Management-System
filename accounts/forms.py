import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

_inp = {
    'style': (
        'width:100%;background:var(--bg-input);border:1px solid var(--border-hi);'
        'border-radius:var(--radius-sm);color:var(--text-1);padding:.65rem .9rem;'
        'font-size:.9rem;outline:none;transition:border-color .2s,box-shadow .2s;'
    )
}


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={**_inp, 'placeholder': 'you@example.com'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={**_inp, 'placeholder': 'Choose a username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={**_inp, 'placeholder': 'Min. 8 characters'}
        )
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={**_inp, 'placeholder': 'Repeat password'}
        )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not re.match(r'^[\w.@+-]+$', username):
            raise forms.ValidationError(
                'Username may only contain letters, digits, and @/./+/-/_ characters.'
            )
        if len(username) < 3:
            raise forms.ValidationError('Username must be at least 3 characters.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email
