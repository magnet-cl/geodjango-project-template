""" Admin base configuration """
from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache

from users.forms import AdminAuthenticationForm
from users.forms import CaptchaAuthenticationForm


class AdminSite(admin.sites.AdminSite):
    login_form = AdminAuthenticationForm

    @never_cache
    def login(self, request, extra_context=None):
        """
        Displays the login form for the given HttpRequest.
        """
        from django.contrib.auth.views import login

        def captched_form(req=None, data=None):
            return CaptchaAuthenticationForm(
                req, data, initial={'captcha': request.META['REMOTE_ADDR']})

        # If the form has been submitted...
        template_name = "accounts/login.jade"

        context = {
            'title': _('Log in'),
            'app_path': request.get_full_path(),
            REDIRECT_FIELD_NAME: request.get_full_path(),
        }
        context.update(extra_context or {})

        login_form = AdminAuthenticationForm

        if request.method == "POST":
            login_try_count = request.session.get('login_try_count', 0)
            request.session['login_try_count'] = login_try_count + 1

            if login_try_count >= 2:
                login_form = captched_form

        defaults = {
            'extra_context': context,
            'current_app': self.name,
            'authentication_form': self.login_form or login_form,
            'template_name': self.login_template or template_name,
        }
        return login(request, **defaults)


class GoogleAdmin(gis_admin.GeoModelAdmin):
    # set the default location
    default_lat = -33.427186
    default_lon = -70.619946
    default_zoom = 11
    extra_js = ["http://maps.googleapis.com/maps/api/js?sensor=false&v=3.6"]
    map_template = 'admin/google_maps.html'

admin.site = AdminSite()
