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

from django.db import models


class Startup(models.Model):
    class Meta:
        app_label = 'app'

    name = models.CharField(max_length=255,db_index=True,unique=True)
    url = models.URLField(max_length=255,unique=True,blank=True,null=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def get_from_mailbox(mailbox):
        if mailbox.startup_id: return mailbox.startup

        obj, created = Startup.objects.get_or_create(name=mailbox.username.capitalize())
        return obj
