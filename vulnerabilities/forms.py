from django import forms
from .models import VulnerabilityReport

_inp = {
    'style': (
        'width:100%;background:var(--bg-input);border:1px solid var(--border-hi);'
        'border-radius:var(--radius-sm);color:var(--text-1);padding:.65rem .9rem;'
        'font-size:.9rem;outline:none;transition:border-color .2s,box-shadow .2s;'
    )
}
_sel = {
    'style': (
        'width:100%;background:var(--bg-input);border:1px solid var(--border-hi);'
        'border-radius:var(--radius-sm);color:var(--text-1);padding:.65rem .9rem;'
        'font-size:.9rem;outline:none;cursor:pointer;appearance:none;'
        'background-image:url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' '
        'width=\'12\' height=\'8\' viewBox=\'0 0 12 8\'%3E%3Cpath d=\'M1 1l5 5 5-5\' '
        'stroke=\'%235c7a96\' stroke-width=\'1.5\' fill=\'none\' stroke-linecap=\'round\'/%3E%3C/svg%3E");'
        'background-repeat:no-repeat;background-position:right .85rem center;padding-right:2.2rem;'
    )
}


class VulnerabilityReportForm(forms.ModelForm):
    """
    `status` is only included for staff users (controlled in __init__) so a
    crafted POST from a regular user cannot escalate or close a report.
    """

    class Meta:
        model = VulnerabilityReport
        fields = ('title', 'severity', 'affected_system', 'description', 'status')
        widgets = {
            'title':           forms.TextInput(attrs={**_inp, 'placeholder': 'Short descriptive title'}),
            'severity':        forms.Select(attrs=_sel),
            'affected_system': forms.TextInput(attrs={**_inp, 'placeholder': 'e.g. Login endpoint, Admin panel'}),
            'description':     forms.Textarea(attrs={**_inp, 'rows': '6',
                                              'placeholder': 'Describe the vulnerability, steps to reproduce, and impact…'}),
            'status':          forms.Select(attrs=_sel),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not (user and user.is_staff):
            self.fields.pop('status')

    def clean_title(self):
        value = self.cleaned_data.get('title', '').strip()
        if len(value) < 5:
            raise forms.ValidationError('Title must be at least 5 characters.')
        if len(value) > 255:
            raise forms.ValidationError('Title must be 255 characters or fewer.')
        return value

    def clean_affected_system(self):
        value = self.cleaned_data.get('affected_system', '').strip()
        if not value:
            raise forms.ValidationError('Affected system is required.')
        if len(value) > 255:
            raise forms.ValidationError('Affected system must be 255 characters or fewer.')
        return value

    def clean_description(self):
        value = self.cleaned_data.get('description', '').strip()
        if len(value) < 20:
            raise forms.ValidationError('Description must be at least 20 characters.')
        return value
