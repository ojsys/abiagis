from django import forms

class ParcelSearchForm(forms.Form):
    file_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    

