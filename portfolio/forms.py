from random import choices

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

class AllAssetsForm(forms.Form):
    # class Meta:
    #     fields = ['start_date', 'end_date', 'interval']
        now = datetime.now()
        default_start = (now - timedelta(days=180)).strftime('%Y-%m-%dT%H:%M')
        default_end = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')

        start_date = forms.DateTimeField(
            initial=default_start,
            widget=forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'min': '2010-01-01T00:00',
                'max': default_end
            })
        )

        end_date = forms.DateTimeField(
            initial=default_end,
            widget=forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'min': '2010-01-01T00:00',
                'max': default_end
            })
        )

        interval = forms.ChoiceField(
            choices=Portfolio.INTERVAL_CHOICES,
            initial='60m',
        )


class AssetAnalysisForm(forms.Form):
    # class Meta:
    #     fields = ['start_date', 'end_date', 'interval']
    now = datetime.now()
    default_start = (now - timedelta(days=180)).strftime('%Y-%m-%dT%H:%M')
    default_end = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')

    start_date = forms.DateTimeField(
        initial=default_start,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'min': '2010-01-01T00:00',
            'max': default_end
        })
    )

    end_date = forms.DateTimeField(
        initial=default_end,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'min': '2010-01-01T00:00',
            'max': default_end
        })
    )

    interval = forms.ChoiceField(
        choices=Portfolio.INTERVAL_CHOICES,
        initial='60m',
    )

    window_size = forms.IntegerField(
        initial=20,
    )


