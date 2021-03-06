from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from pt.models import PtTest, PtScore, GENDER_CHOICES
from personnel.models import Cadet

from Utils.widgets.date_picker import DatePicker

from collections import OrderedDict


class TestForm(forms.ModelForm):

    date = forms.CharField(widget=DatePicker())

    class Meta():
        model = PtTest
        exclude = []

    test_already_exists = ValidationError(
        'A test has already been created for that date.',
        code='invalid'
    )

    def clean(self):
        test_date = self.cleaned_data.get('date', '')
        tests = PtTest.objects.filter(date__exact=test_date)
        if tests:
            if tests[0].id != self.instance.id:
                self.add_error('date', self.test_already_exists)
                print self.errors

class ScoreForm(forms.Form):
    cadet = forms.CharField()
    cadet_id = forms.CharField(widget=forms.HiddenInput(attrs={'class': 'cadet_id'}), required=False)
    pushups = forms.IntegerField(initial=None,
                                 widget=forms.NumberInput(attrs={'placeholder': 0, "style": "width: 125px"}))
    situps = forms.IntegerField(initial=None,
                                widget=forms.NumberInput(attrs={'placeholder': 0, "style": "width: 125px"}))
    two_mile = forms.CharField(initial=None,
                               widget=forms.TextInput(attrs={'placeholder': '00:00', "style": "width: 125px"}))

    invalid_name = ValidationError(
            'Invalid cadet name. Check for spelling and ensure that the cadet has a profile made',
            code='invalid',
    )

    invalid_run_time = ValidationError(
        'Invalid Run Time Format',
        code='invalid'
    )

    def clean_cadet_id(self):
        if not self.cleaned_data.get('cadet_id') and self.cleaned_data.get('cadet'):
            self.add_error('cadet', self.invalid_name)

        try:
            if self.cleaned_data.get('cadet_id'):
                Cadet.objects.get(id=int(self.cleaned_data.get('cadet_id')))
        except ObjectDoesNotExist:
            self.add_error('cadet', self.invalid_name)

        return self.cleaned_data.get('cadet_id')

    def clean_two_mile(self):

        if not PtScore.valid_run_time(self.cleaned_data.get('two_mile')):
            self.add_error('two_mile', self.invalid_run_time)

        return self.cleaned_data.get('two_mile')


class ScoreCalculatorForm(ScoreForm):
    cadet = None
    cadet_id = None
    age = forms.IntegerField(initial=None, widget=forms.NumberInput(attrs={'placeholder': 0}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES)

    def __init__(self, *args, **kwargs):
        super(ScoreCalculatorForm, self).__init__(*args, **kwargs)
        fields = OrderedDict()
        fields.update({'gender': self.fields['gender']})
        fields.update({'age': self.fields['age']})
        fields.update({'pushups': self.fields['pushups']})
        fields.update({'situps': self.fields['situps']})
        fields.update({'two_mile': self.fields['two_mile']})
        self.fields = fields