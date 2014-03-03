# -*- coding: utf-8 -*-

# models
from users.models import User

# forms
from base.forms import BaseModelForm

from base.fields import ReCaptchaField
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import loader
from django.utils.http import int_to_base36
from django.utils.translation import ugettext_lazy as _
from django import forms


class AuthenticationForm(forms.Form):
    """ Custom class for authenticating users. Takes the basic
    AuthenticationForm and adds email as an alternative for login
    """
    email = forms.EmailField(label=_("Email"), required=True)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct email and password. "
                           "Note that both fields may be case-sensitive."),
        'no_cookies': _("Your Web browser doesn't appear to have cookies "
                        "enabled. Cookies are required for logging in."),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        validates the email and password.
        """
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'])
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(self.error_messages['no_cookies'])

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class CaptchaAuthenticationForm(AuthenticationForm):
    """ a user authentication form with a captcha """
    captcha = ReCaptchaField(
        label="¿Eres humano?",
    )


class AdminAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form used in the admin app.

    """
    error_messages = {
        'required': _("Please log in again, because your session has expired.")
    }
    this_is_the_login_form = forms.BooleanField(
        widget=forms.HiddenInput, initial=1, error_messages=error_messages)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        message = _("Please enter the correct email and password for a staff "
                    "account. Note that both fields may be case-sensitive.")

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(message)
            elif not self.user_cache.is_active or not self.user_cache.is_staff:
                raise forms.ValidationError(message)
        self.check_for_test_cookie()
        return self.cleaned_data


class UserCreationForm(BaseModelForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    error_messages = {
        'duplicate_email': _("A user with that email already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    email = forms.EmailField(
        label=_("E-mail"), max_length=75,
        help_text=_("Enter the same password as above, for verification."),
    )
    first_name = forms.CharField(
        label=_("first name").capitalize(),
        help_text=_("The name of the user"),
    )
    last_name = forms.CharField(
        label=_("last name").capitalize(),
        help_text=_("The last name of the user"),
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput, required=False,
        help_text=_("Enter the same password as above, for verification."),
    )

    class Meta:
        model = User
        fields = ("email",)

    def clean_email(self):
        """ checks that the email is unique """
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean_password2(self):
        """ check that the password was correctly repeated """

        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, verify_email_address=False, domain_override=None,
             subject_template_name='emails/user_new_subject.txt',
             email_template_name='emails/user_new.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, commit=True):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.active = not verify_email_address

        if commit:
            user.save()

        if verify_email_address:
            from django.core.mail import send_mail

            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain

            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, from_email, [user.email])

        return user


class CaptchaUserCreationForm(UserCreationForm):
    """ a user creation form with a captcha """
    captcha = ReCaptchaField(
        label="¿Eres humano?",
    )


class UserChangeForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = ('password',)

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')
