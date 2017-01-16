"""
Copyright (c) 2016-2017 Kima Ventures
Reporting system for VC funds

This is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms


@login_required
def index(request):
    return HttpResponseRedirect(reverse("settings_password"))

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput,label="Current password")
    new_password1 = forms.CharField(widget=forms.PasswordInput,label="New password")
    new_password2 = forms.CharField(widget=forms.PasswordInput,label="New password (again)")

    def __init__(self, user, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        if not self.user.check_password(self.cleaned_data["current_password"]):
            raise forms.ValidationError("Current password incorrect")

        return self.cleaned_data["current_password"]

    def clean(self):
        if 'new_password1' in self.cleaned_data and 'new_password2' in self.cleaned_data:
            if self.cleaned_data['new_password1'] != self.cleaned_data['new_password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return self.cleaned_data

@login_required
def password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            u = request.user
            u.set_password(form.cleaned_data["new_password1"])
            u.save()

            messages.success(request, "Your password has been successfully updated !")

            form = PasswordChangeForm(request.user) # Clean the form content
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'settings/password.html', {'form': form})