################################################
#
# These views handle everything that has to do 
# with the login and the user
#
################################################

from django.conf import settings
from django.shortcuts import render, redirect, resolve_url
from hrcompass.forms import UserForm
from django.contrib.auth.models import User
from django.views.generic import FormView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from two_factor.views.utils import class_view_decorator
from django.views.decorators.cache import never_cache
from two_factor.views import OTPRequiredMixin
from django_otp.decorators import otp_required
from django.contrib.auth.decorators import login_required
from two_factor.utils import default_device
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

@otp_required
def logincomplete(request):
    return redirect("/show")

# Show OTP activation if it is not
@login_required
def profile(request):
    user = request.user
    #print(user.is_verified())
    if user.is_verified():
        return redirect("/show")
    else:
        return render(request,"profile.html")

@otp_required
def changepassword(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        form = UserForm(request.POST, instance = user)
        newemail = request.POST.get('email')
        newpassword = request.POST.get('password')
        verifypassword = request.POST.get('verifypassword')
        if newpassword == verifypassword:
            if form.is_valid():
                #user = form.save(commit=True)
                if newpassword == "" and newemail == "":
                    messages.success(request, 'Please enter data!')
                    return redirect("../%2Faccount/two_factor/")
                else:
                    if newemail != "":
                        user.save(update_fields=["email"])
                        messages.success(request, 'Your Email was successfully updated!')
                    if newpassword != "":
                        user.set_password(newpassword)
                        user.save(update_fields=["password"])
                        update_session_auth_hash(request, user)  # Important!
                        messages.success(request, 'Your password was successfully updated!')
                    return redirect('/show')
            else:
                messages.error(request, 'The form is invalid')
        else:
            messages.error(request, 'The password do not match')
    else:
        form = ProfileView(request.user)
    return redirect("../%2Faccount/two_factor/")





@class_view_decorator(never_cache)
class HomeView(OTPRequiredMixin, TemplateView):
    template_name = 'show.html'

class RegistrationView(FormView):
    template_name = 'registration.html'
    form_class = UserCreationForm

    def form_valid(self, form):
        form.save()
        return redirect('registration_complete')

class RegistrationCompleteView(TemplateView):
    template_name = 'registration_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        return context

@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class ProfileView(TemplateView):
    """
    View used by users for managing two-factor configuration.
    This view shows whether two-factor has been configured for the user's
    account. If two-factor is enabled, it also lists the primary verification
    method and backup verification methods.
    """
    template_name = 'profile.html'
    
    def get_context_data(self, **kwargs):
        try:
            backup_tokens = self.request.user.staticdevice_set.all()[0].token_set.count()
        except Exception:
            backup_tokens = 0
        form = UserForm()
        return {
            'default_device': default_device(self.request.user),
            'default_device_type': default_device(self.request.user).__class__.__name__,
            'form': form,
        }