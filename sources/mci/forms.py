from django.forms import ModelForm, PasswordInput
from mci.models import MCIUser


class MCIUserForm(ModelForm):
    class Meta:
        model = MCIUser
        widgets = {
            'password' : PasswordInput(),
        }