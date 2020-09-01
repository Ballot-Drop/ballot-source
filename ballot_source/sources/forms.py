import requests
from django import forms
from django.core.exceptions import ValidationError

from .models import Source


class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ["url", "source_type", "fips", "state"]

    def clean_url(self):
        self.cleaned_data = super(SourceForm, self).clean()
        url = self.cleaned_data["url"]

        Source.validate_url(url)

        try:
            requests.get(url)
        except requests.exceptions.ConnectionError:
            raise ValidationError(
                "The url does not appear to be working. Check the spelling and try again."
            )
        return url
