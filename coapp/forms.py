from django import forms

class ParcelSearchForm(forms.Form):
    file_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    

class MergePDFForm(forms.Form):
    file1 = forms.FileField(label='Select File 1', widget=forms.FileInput(attrs={'class':'form-control'}))
    file2 = forms.FileField(label='Select File 2', widget=forms.FileInput(attrs={'class':'form-control'}))