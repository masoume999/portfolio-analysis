from django import forms
from .models import Portfolio, Asset
from datetime import datetime, timedelta

class PortfolioForm(forms.ModelForm):
    selected_assets = forms.ModelMultipleChoiceField(
        queryset=Asset.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Selected assets"
    )

    class Meta:
        model = Portfolio
        fields = ['selected_assets', 'interval', 'start_date', 'end_date']
        widgets = {'start_date': forms.DateInput(attrs={'type': 'datetime-local',
                                                        'min': '2010-01-01T00:00',
                                                        'max': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT23:59')}),
                   'end_date': forms.DateInput(attrs={'type': 'datetime-local',
                                                      'min': '2010-01-01T00:00',
                                                      'max': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT23:59')})
                   }
