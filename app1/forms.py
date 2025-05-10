from django import forms
from .models import Appointment
from datetime import date, datetime, time

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude = ['advocate']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-control'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'cols': 40,
                'placeholder': 'Enter a brief reason...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        self.fields['appointment_date'].widget = forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
                'min': today.isoformat()
            }
        )
        self.fields['appointment_time'].widget = forms.TimeInput(
            attrs={
                'class': 'form-control',
                'type': 'time'
            }
        )
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (
                forms.TextInput, forms.EmailInput, forms.DateInput,
                forms.TimeInput, forms.Textarea, forms.Select
            )):
                field.widget.attrs['class'] = 'form-control'

    # ✅ THIS NEEDS TO BE INDENTED HERE
    def clean(self):
        cleaned_data = super().clean()
        appt_date = cleaned_data.get('appointment_date')
        appt_time = cleaned_data.get('appointment_time')

        if not appt_date or not appt_time:
            return

        appt_datetime = datetime.combine(appt_date, appt_time)
        now = datetime.now()

        if appt_datetime < now:
            raise forms.ValidationError("You cannot book a time in the past.")

        # Avoid conflict with other appointments
        conflict = Appointment.objects.filter(
            appointment_date=appt_date,
            appointment_time=appt_time
        ).exclude(pk=self.instance.pk).exists()

        if conflict:
            raise forms.ValidationError("This time slot is already booked. Please choose another.")

        return cleaned_data





