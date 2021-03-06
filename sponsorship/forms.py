# coding: utf8
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from .models import Sponsorship, SponsorRequest


class SponsorForm(forms.ModelForm):
    runner = forms.ModelChoiceField(label=_("Runner"),
                                    queryset=get_user_model().objects.all(),
                                    required=False)
    sponsor = forms.ModelChoiceField(label=_("Sponsor"),
                                     queryset=get_user_model().objects.all(),
                                     required=False)
    rate = forms.FloatField(label=_("Rate (DKK per km)"),
                            widget=forms.TextInput(
                                attrs={'class': 'form-control'}),
                            localize=True)
    start_date = forms.DateField(label=_("Sponsorship start date"),
                                 required=True,
                                 widget=forms.DateInput(attrs={'class': 'form-control',
                                                               'id': 'start_datepicker',
                                                                        'autocomplete': "off"}),
                                 )
    end_date = forms.DateField(label=_("Sponsorship end date (optional)"),
                               required=False,
                               widget=forms.DateInput(attrs={'class': 'form-control',
                                                             'id': 'end_datepicker',
                                                             'autocomplete': 'off'}),
                               )
    max_amount = forms.FloatField(label=_("Maximum amount (optional)"),
                                  required=False,
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control'}),
                                  localize=True)

    class Meta:
        model = Sponsorship
        fields = ['runner', 'sponsor', 'rate', 'start_date', 'end_date', 'max_amount']

    def is_valid(self):

        valid = super(SponsorForm, self).is_valid()

        if not valid:
            return valid

        if self.cleaned_data['rate'] < 0:
            self.add_error('rate', _('Rate cannot be negative'))
            valid = False

        if self.cleaned_data['max_amount'] and \
           self.cleaned_data['max_amount'] < 0:
            self.add_error('max_amount', _('Max amount cannot be negative'))
            valid = False

        if self.cleaned_data['end_date'] and \
           self.cleaned_data['start_date'] > self.cleaned_data['end_date']:
            self.add_error('end_date', _('End date cannot be before start date.'))
            valid = False

        return valid
