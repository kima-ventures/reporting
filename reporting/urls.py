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
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from app import views as app_views
from app import views_admin as app_views_admin
from app import views_settings as app_views_settings
from app.views import KimaLoginForm

urlpatterns = [
    url(r'^$', login_required(RedirectView.as_view(url="/startup/")), name="index"),

    url(r'^startup/$', app_views.startup_list, name="startup_list"),
    url(r'^startup/(?P<id>[0-9]+)/$', app_views.startup_detail, name="startup_detail"),
    url(r'^message/(?P<id>[0-9]+)/$', app_views.message_detail, name="message_detail"),
    url(r'^message/(?P<id>[0-9]+)/attachment/(?P<attachment_id>[0-9]+)/$', app_views.message_attachment, name="message_attachment"),

    url(r'^accounts/login/$', auth_views.login, {'template_name': 'registration/login.html', 'authentication_form': KimaLoginForm}, name="auth_login"),
    url(r'^accounts/logout/$', auth_views.logout,  name='auth_logout'),

    url(r'^!callback/mail/(?P<pwd>[0-9A-Za-z]+)/$', app_views.incoming_callback, name="mail_callback"),

    url(r'^settings/$', app_views_settings.index, name="settings"),
    url(r'^settings/password/$', app_views_settings.password, name="settings_password"),

    url(r'^admin/$', app_views_admin.index, name="admin"),
    url(r'^admin/user/$', app_views_admin.user_list, name="admin_user_list"),
    url(r'^admin/user/(?P<user_id>[0-9]+)/$', app_views_admin.user_edit, name="admin_user_edit"),
    url(r'^admin/user/!add/$', app_views_admin.user_add, name="admin_user_add"),

    url(r'^admin/startup/$', app_views_admin.startup_list, name="admin_startup_list"),
    url(r'^admin/startup/(?P<startup_id>[0-9]+)/permission/$', app_views_admin.startup_permission, name="admin_startup_permission"),
    url(r'^admin/startup/(?P<startup_id>[0-9]+)/edit/$', app_views_admin.startup_edit, name="admin_startup_edit"),

    url(r'^django_admin/', admin.site.urls),
]
