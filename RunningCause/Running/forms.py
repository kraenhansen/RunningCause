from django import forms
from django.contrib.admin import widgets
from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker'})

class SponsorForm(forms.Form):
    # sponsor_name = forms.CharField(label="Sponsor name", max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    rate = forms.FloatField(label="Rate", widget=forms.TextInput(attrs={'class':'form-control'}))
    sponsor_email = forms.EmailField(label="Your email", max_length = 100, widget=forms.TextInput(attrs={'class':'form-control'}))
    end_date = forms.DateField(label="Sponsorship end date", widget=forms.DateInput(attrs={'class':'form-control', 
                                                                                            'id':'datepicker', 
                                                                                            'autocomplete':"off"}))
    max_amount = forms.IntegerField(label="Maximum total amount", widget=forms.TextInput(attrs={'class':'form-control'}))

class RunInputForm(forms.Form):
    distance = forms.FloatField(label="Distance in km", widget=forms.TextInput(attrs={'class':'form-control'}))
    date = forms.DateField(label="Run date", widget=forms.DateInput(attrs={'class':'form-control', 
                                                                            'id':'datepicker', 
                                                                            'autocomplete':"off"}))