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

class Mailbox(models.Model):
    class Meta:
        app_label = 'app'

    # Mailbox is != than Startup so you can have multiple mailboxes per startup if they change name or do spelling mistakes

    username = models.CharField(max_length=255,db_index=True,unique=True)

    startup = models.ForeignKey('Startup')

    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        from app.models.startup import Startup

        # Attach to a startup
        if not self.startup_id: self.startup = Startup.get_from_mailbox(self)
        return super(Mailbox, self).save(*args, **kwargs)

    @staticmethod
    def get_from_message(msg):
        if msg.mailbox_id: return msg.mailbox

        username = (u''.join(msg.rcpt_to.split('@')[:-1])).split('+')[0][:255]
        obj,created = Mailbox.objects.get_or_create(username=username)

        return obj