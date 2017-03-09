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

import email, json, datetime
import os
from email.header import decode_header
from django import forms

from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from app.models import Message, Startup
from app.models import StartupPermission
from app.models import UserProfile
from app.utils import user_has_access


@login_required
def startup_list(request):
    startup_list = []

    for startup in Startup.objects.all().annotate(latest_mail=Max('mailbox__message__created_at')).order_by('-latest_mail'):
        if user_has_access(request, startup):
            startup.authorized_users = StartupPermission.users_allowed(startup)

            startup_list.append(startup)

    return render(request, "messages/startup_list.html", {"startup_list": startup_list,
                                                          "warning_date": (timezone.now()-datetime.timedelta(days=60)).isoformat()})

@login_required
def startup_detail(request, id):
    startup = get_object_or_404(Startup, id=id)
    if not user_has_access(request, startup): return HttpResponseRedirect("/")

    messages = Message.objects.filter(mailbox__startup=startup).order_by('-created_at')

    return render(request, "messages/startup_detail.html", {"startup": startup, "messages": messages})

@login_required
def message_detail(request, id):
    def _decode_header(txt):
        dh = decode_header(txt)
        default_charset = 'ASCII'
        return u''.join([unicode(t[0], t[1] or default_charset) for t in dh])

    message_db = get_object_or_404(Message, id=id)
    if not user_has_access(request, message_db.mailbox.startup): return HttpResponseRedirect("/")

    message_obj = email.message_from_string(message_db.messagecontent.email)
    message = {
        "from": message_obj["From"],
        "to": message_obj["To"],
        "cc": message_obj["Cc"],
        "subject": _decode_header(message_obj["Subject"]),
        "date": message_obj["Date"],
        "attachments": message_db.get_attachment_list(),
        "plaintext": "",
        "html": ""
    }

    for part in message_obj.walk():
        if part.get_content_type() == "text/plain":
            message["plaintext"] += part.get_payload(decode=True)
            if part.get_content_charset() is not None:
                message["plaintext"] = message["plaintext"].decode(part.get_content_charset())

        elif part.get_content_type() == "text/html":
            message["html"] += part.get_payload(decode=True)
            if part.get_content_charset() is not None:
                message["html"] = message["html"].decode(part.get_content_charset())

    if len(message["plaintext"]) == 0: message["plaintext"] = None
    if len(message["html"]) == 0: message["html"] = None

    return render(request, "messages/message_detail.html", {"message_db": message_db, "message": message})

@login_required
def message_attachment(request, id, attachment_id):
    message_db = get_object_or_404(Message, id=id)
    if not user_has_access(request, message_db.mailbox.startup): return HttpResponseRedirect("/")

    attachment = message_db.get_attachment(attachment_id)

    response = HttpResponse(attachment["data"], content_type=attachment["content_type"])

    # TODO: Should be better to escape than remove
    response['Content-Disposition'] = u'filename="{0}"'.format(attachment["filename"].replace('"',''))

    return response

@csrf_exempt
def incoming_callback(request, pwd):
    if pwd != os.getenv('CALLBACK_EMAIL_PASSWORD', None): return HttpResponseRedirect('/')
    if request.method != 'POST': return HttpResponseRedirect('/')

    msg = Message()
    msg.import_from_sendgrid(
        email=request.POST.get("email"),
        mail_from=request.POST.get("from"),
        to=json.loads(request.POST.get("envelope"))["to"][0].lower(),
        subject=request.POST.get("subject")
    )
    msg.relay_email()

    return HttpResponse("ok")

class KimaLoginForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': '', 'class': 'form-control'}),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
    )