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

from django.http import HttpResponseRedirect

from app.models import StartupPermission


def user_has_access(request, startup, userprofile=None):
    return StartupPermission.has_user_permission(request.user, startup, userprofile)

def staff_required(view):
    def f(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseRedirect("/")
        return view(request, *args, **kwargs)

    return f