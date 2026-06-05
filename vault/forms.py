from django import forms
from .models import Credential

_inp = {
    'style': (
        'width:100%;background:var(--bg-input);border:1px solid var(--border-hi);'
        'border-radius:var(--radius-sm);color:var(--text-1);padding:.65rem .9rem;'
        'font-size:.9rem;outline:none;transition:border-color .2s,box-shadow .2s;'
    )
}


class CredentialForm(forms.ModelForm):
    class Meta:
        model = Credential
        fields = ('site_name', 'username', 'password', 'notes')
        widgets = {
            'site_name': forms.TextInput(attrs={**_inp, 'placeholder': 'e.g. github.com'}),
            'username':  forms.TextInput(attrs={**_inp, 'placeholder': 'Login username or email'}),
            'password':  forms.PasswordInput(attrs={**_inp, 'id': 'id_password'}, render_value=True),
            'notes':     forms.Textarea(attrs={**_inp, 'rows': '3', 'placeholder': 'Optional notes'}),
        }
        labels = {'site_name': 'Site / Service'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # When editing, pre-fill with decrypted password so the form shows plaintext.
        # The model's save() will re-encrypt whatever is submitted.
        if self.instance and self.instance.pk:
            self.initial['password'] = self.instance.decrypted_password

    def clean_site_name(self):
        value = self.cleaned_data.get('site_name', '').strip()
        if not value:
            raise forms.ValidationError('Site name is required.')
        if len(value) > 255:
            raise forms.ValidationError('Site name must be 255 characters or fewer.')
        return value

    def clean_username(self):
        value = self.cleaned_data.get('username', '').strip()
        if not value:
            raise forms.ValidationError('Username is required.')
        if len(value) > 255:
            raise forms.ValidationError('Username must be 255 characters or fewer.')
        return value

    def clean_password(self):
        value = self.cleaned_data.get('password', '').strip()
        if not value:
            raise forms.ValidationError('Password is required.')
        if len(value) > 500:
            raise forms.ValidationError('Password exceeds the maximum allowed length.')
        return value
