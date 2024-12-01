# forms.py
from django import forms

class TableCreationForm(forms.Form):
    table_name = forms.CharField(label='Table Name', max_length=100)

class FieldCreationForm(forms.Form):
    field_name = forms.CharField(label='Field Name', max_length=100)
    field_type = forms.ChoiceField(choices=[
        ('CharField', 'CharField'),
        ('TextField', 'TextField'),
        ('IntegerField', 'IntegerField'),
        ('BooleanField', 'BooleanField'),
        ('DateField', 'DateField'),
        ('DateTimeField', 'DateTimeField'),
        ('EmailField', 'EmailField'),
        ('FloatField', 'FloatField'),
        ('DecimalField', 'DecimalField'),
    ])
    max_length = forms.IntegerField(required=False, label='Max Length (for CharField only)')

