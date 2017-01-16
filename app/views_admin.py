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

import shortuuid
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.models import StartupPermission, UserProfile, Startup
from app.utils import staff_required

@login_required
@staff_required
def index(request):
    return HttpResponseRedirect(reverse("admin_user_list"))

class UserCreateForm(forms.Form): # TODO : Look if it's not better to subclass a ModelForm to user, and add a custom field around it
    first_name = forms.CharField(label='First name', max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label='Last name', max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label='Email', max_length=255, widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(label='Password', max_length=255, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    permission_mode = forms.ChoiceField(label='Permission mode',choices=UserProfile.PERMISSION_CHOICES,initial=UserProfile.PERMISSION_ALLOW_DEFAULT, widget=forms.Select(attrs={"class": "form-control"}))
    relay_email = forms.BooleanField(label='Relay by e-mail',initial=True,widget=forms.CheckboxInput(),required=False)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("This user already exists")
        return email

class UserEditForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label='Last name', max_length=255, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label='Email', max_length=255, widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(label='Password', max_length=255, required=False, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    permission_mode = forms.ChoiceField(label='Permission mode',choices=UserProfile.PERMISSION_CHOICES,initial=UserProfile.PERMISSION_ALLOW_DEFAULT, widget=forms.Select(attrs={"class": "form-control"}))
    relay_email = forms.BooleanField(label='Relay by e-mail', initial=True,widget=forms.CheckboxInput(),required=False)

@login_required
@staff_required
def user_list(request):
    users = User.objects.filter(is_active=True).order_by('first_name')

    startup_per_user = {}
    for user in users:
        startup_per_user[user.id] = StartupPermission.startups_allowed(user).count()

    return render(request, "admin/admin_user_list.html", {"users": users,
                                                          "startup_per_user": startup_per_user,
                                                          "cur_admin_page": "user"})

@login_required
@staff_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST)

        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            if form.cleaned_data.get('password', None):
                user.set_password(form.cleaned_data['password'])
            user.save()

            up = user.userprofile
            up.permission_mode = form.cleaned_data['permission_mode']
            up.relay_email = form.cleaned_data['relay_email']
            up.save()

            return HttpResponseRedirect(reverse("admin_user_list"))
    else:
        form = UserEditForm(initial={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "password": user.password,
            "permission_mode": user.userprofile.permission_mode,
            "relay_email": user.userprofile.relay_email
        })

    return render(request, "admin/admin_user_detail.html", {"form": form, "create": False})

@login_required
@staff_required
def user_add(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            u = User(
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name'],
                email = form.cleaned_data['email'],
                is_active = True
            )

            # Generate the username
            username = None
            while True:
                username = shortuuid.ShortUUID().random(length=25).upper()
                if not get_user_model().objects.filter(username=username).exists():
                    break
            u.username = username

            u.set_password(form.cleaned_data['password'])
            u.save()

            up = UserProfile(
                permission_mode = form.cleaned_data['permission_mode']
            )
            up.user = u
            up.save()

            return HttpResponseRedirect(reverse("admin_user_list"))
    else:
        form = UserCreateForm()
    return render(request, "admin/admin_user_detail.html", {"form": form, "create": True})

@login_required
@staff_required
def startup_list(request):
    startups = Startup.objects.all().order_by('name')

    # TODO : This might not be efficient enough
    user_permissions = {}
    user_list = User.objects.filter(is_active=True)
    for startup in startups:
        permission_map = []
        for user in user_list:
            permission_map.append((user,StartupPermission.has_user_permission(user, startup)))
        user_permissions[startup.id] = permission_map

    return render(request, "admin/admin_startup_list.html", {"startups": startups,
                                                             "user_permissions": user_permissions,
                                                             "cur_admin_page": "startup"})


class StartupPermissionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    has_permission = serializers.BooleanField()

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User doesn't exist")
        return value

@login_required
@staff_required
@api_view(['POST'])
def startup_permission(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)

    data = StartupPermissionSerializer(data=request.data)
    if not data.is_valid():
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(id=data.data['user_id'])
    has_permission = data.data['has_permission']

    # Figure out if we need to delete or to add the permission in the table
    if user.userprofile.permission_mode == UserProfile.PERMISSION_ALLOW_DEFAULT:
        need_to_add = not has_permission
    else:
        need_to_add = has_permission

    # Then do the operation in the DB
    if need_to_add:
        StartupPermission.objects.get_or_create(user=user,startup=startup)
    else:
        sp = StartupPermission.objects.filter(user=user,startup=startup).first()
        if sp:
            sp.delete()

    return Response({"ok": True})

class StartupEditSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()

    def validate_key(self, key):
        if key not in ["name", "url"]:
            raise serializers.ValidationError("Key is invalid")
        return key

@login_required
@staff_required
@api_view(['POST'])
def startup_edit(request, startup_id):
    startup = get_object_or_404(Startup, id=startup_id)

    data = StartupEditSerializer(data=request.data)
    if not data.is_valid():
        return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)

    if not "key" in request.POST or not "value" in request.POST:
        raise Http404()

    if data.data["key"] == "name":
        startup.name = data.data["value"]
    elif data.data["value"] == "url":
        startup.url = data.data["value"]

    startup.save()

    return Response({"ok": True})