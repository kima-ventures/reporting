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

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.core.cache import cache

from app.models.startup import Startup


class StartupPermission(models.Model):
    """
    If the user is on allow default mode -> it says the user cannot see this startup
    If the user is on deny default mode -> it says the user can see this startup
    """
    class Meta:
        unique_together = (("user", "startup"),)

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    startup = models.ForeignKey('Startup')

    @staticmethod
    def has_user_permission(user, startup, userprofile=None):
        cache_key = u"has_user_permission|{0}|{1}".format(user.id,startup.id)
        if cache.get(cache_key):
            return cache.get(cache_key)

        from app.models.userprofile import UserProfile
        if not userprofile:
            userprofile = UserProfile.objects.get_or_create(user=user)[0]

        if userprofile.permission_mode == UserProfile.PERMISSION_ALLOW_DEFAULT:
            has_user_permission = (not StartupPermission.objects.filter(user=user, startup=startup).exists())
        else:
            has_user_permission = (StartupPermission.objects.filter(user=user, startup=startup).exists())

        cache.set(cache_key, has_user_permission, 5) # 5 secs cache
        return has_user_permission

    @staticmethod
    def startups_allowed(user):
        from app.models.userprofile import UserProfile
        userprofile = UserProfile.objects.get_or_create(user=user)[0]

        startup_permission_ids = StartupPermission.objects.filter(user=user).values_list('startup_id', flat=True)

        if userprofile.permission_mode == UserProfile.PERMISSION_ALLOW_DEFAULT:
            return Startup.objects.exclude(id__in=startup_permission_ids)
        else:
            return Startup.objects.filter(id__in=startup_permission_ids)

    @staticmethod
    def users_allowed(startup):
        users_allowed = []
        for u in get_user_model().objects.filter(is_active=True):
            if StartupPermission.has_user_permission(u, startup):
                users_allowed.append(u)

        return users_allowed