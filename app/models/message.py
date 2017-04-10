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

import email
import os
import smtplib

from django.conf import settings
from django.db import models

from app.models.messagecontent import MessageContent


class Message(models.Model):
    class Meta:
        get_latest_by = "created_at"
        app_label = 'app'

    mailbox = models.ForeignKey('Mailbox')

    tag = models.CharField(max_length=255,blank=True,null=True)

    mail_from_name = models.CharField(max_length=255)
    mail_from = models.EmailField()
    rcpt_to = models.EmailField()
    subject = models.TextField()

    message_id = models.CharField(max_length=255,null=True,default=None,db_index=True)
    in_reply_to = models.CharField(max_length=255,null=True,default=None)
    references = models.CharField(max_length=255,null=True,default=None)

    has_attachment = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from app.models.mailbox import Mailbox

        # Attach to a mailbox
        if not self.mailbox_id: self.mailbox = Mailbox.get_from_message(self)
        return super(Message, self).save(*args, **kwargs)

    def get_attachment_list(self):
        emailobj = email.message_from_string(self.messagecontent.email)
        attachments = []
        id = 0

        payload_list = emailobj.get_payload()
        if isinstance(payload_list, str): # If get_payload() is a string, it's not a multipart message, hence no attached files
            return []

        for payload in payload_list:
            if payload.get_filename():
                attachments.append(
                    {"id": id,
                     "filename": payload.get_filename(),
                     "content_type": payload.get_content_type()})
            id += 1
        return attachments

    def get_attachment(self, id):
        emailobj = email.message_from_string(self.messagecontent.email)
        payload = emailobj.get_payload()

        id = int(id)

        if id >= len(payload):
            return None

        if not payload[id].get_filename():
            return None

        return {"filename": payload[id].get_filename(),
                "content_type": payload[id].get_content_type(),
                "data":payload[id].get_payload(decode=True)}

    def import_from_sendgrid(self, **kwargs):
        self.mail_from_name = email.utils.parseaddr(kwargs['mail_from'])[0]
        self.mail_from = email.utils.parseaddr(kwargs['mail_from'].lower())[1]

        self.rcpt_to = email.utils.parseaddr(kwargs['to'].lower())[1]
        self.tag = self.rcpt_to.split('+')[1].split('@')[0] if '+' in self.rcpt_to else None

        self.subject = kwargs['subject']

        self.messagecontent = MessageContent()
        self.messagecontent.email = kwargs['email'].encode('utf-8')

        # Parse message_id and has_attachment from the email
        emailobj = email.message_from_string(self.messagecontent.email)
        emailheaders = dict(emailobj)

        self.message_id = emailheaders.get("Message-ID")

        self.in_reply_to = emailheaders.get("In-Reply-To")
        if self.in_reply_to is not None: self.in_reply_to = self.in_reply_to[:255]

        self.references = emailheaders.get("References")
        if self.references is not None: self.references = self.references[:255]

        for part in emailobj.walk():
            c_disp = part.get_param('attachment', None, 'content-disposition')
            if c_disp is not None:
                self.has_attachment = True

        self.save()
        self.messagecontent.message = self
        self.messagecontent.save()

    def relay_email(self):
        from app.models import StartupPermission

        mail_to = []
        for u in StartupPermission.users_allowed(self.mailbox.startup):
            if u.userprofile.relay_email:
                mail_to.append(u.email)

        # Edit the subject
        prepend_with = u"[{0}-Reporting] [{1}] ".format(os.getenv("FUND_NAME", "Kima"),
                                                        self.mailbox.startup.name)
        e = email.message_from_string(self.messagecontent.email)
        if not prepend_with in self.subject:
            del e["Subject"]
            e["Subject"] = prepend_with+self.subject

        # TODO : See if it's possible to access the raw SMTP object within Django
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(self.mail_from.encode('utf-8'), map(lambda x : x.encode('utf-8'), mail_to), e.as_string())
        server.quit()