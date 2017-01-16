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
from django.db import models


class UserProfile(models.Model):
    class Meta:
        app_label = 'app'

    PERMISSION_ALLOW_DEFAULT = 0
    PERMISSION_DENY_DEFAULT = 1
    PERMISSION_CHOICES = (
        (PERMISSION_ALLOW_DEFAULT, "Allow default"),
        (PERMISSION_DENY_DEFAULT, "Deny default")
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    permission_mode = models.IntegerField(choices=PERMISSION_CHOICES,default=PERMISSION_ALLOW_DEFAULT)
    relay_email = models.BooleanField(default=True)