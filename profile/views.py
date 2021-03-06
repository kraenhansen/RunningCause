# coding: utf8
import logging

import stripe
import mailchimp

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import url
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model, REDIRECT_FIELD_NAME
from django.utils.http import is_safe_url

from allauth.account.forms import LoginForm, SignupForm
import cloudinary

from .forms import UserProfileForm
from .models import User
from django.db.models import Sum

# TODO: I wonder if there is a better way that makes the apps
# more decoupled.
from challenges.models import Challenge


log = logging.getLogger(__name__)


def users_list(request):
    user_list = get_user_model().objects.verified_users().order_by('username')
    context = {
       'user_list': user_list,
    }
    return render(request, 'profile/users_list.html', context)


def overview(request, user_id=None):
    person = get_object_or_404(get_user_model(), id=user_id)
    total_distance = person.runs.all().aggregate(x=Sum('distance'))['x'] or 0

    sponsorships = person.sponsorships_recieved.all()
    amount_earned = 0
    for sponsorship in sponsorships:
        amount_earned = amount_earned + sponsorship.total_amount

    sponsorships_given = person.sponsorships_given.all()
    total_amount = 0
    total_amount_donated = 0
    for sponsorship in sponsorships_given:
        total_amount += sponsorship.total_amount
        total_amount_donated += sponsorship.amount_paid

    challenges_recieved = person.challenges_recieved.all().order_by('end_date')

    own_page = False
    if request.user.is_authenticated():
        own_page = request.user == person

    context = {
        'total_distance': total_distance,
        'sponsorships': sponsorships,
        'amount_earned': amount_earned,
        'total_amount_donated': total_amount_donated,
        'challenges_recieved': challenges_recieved,
        'own_page': own_page,
        'person': person,
        'tab_name': 'overview',
    }
    return render(request, 'profile/overview.html', context)


def user_raised(request, user_id=None):
    person = get_object_or_404(get_user_model(), id=user_id)
    sponsorships = person.sponsorships_recieved.all()
    amount_earned = 0
    for sponsorship in sponsorships:
        amount_earned = amount_earned + sponsorship.total_amount

    challenges_recieved = person.challenges_recieved.all().order_by('end_date')

    own_page = False
    if request.user.is_authenticated():
        own_page = request.user == person

    context = {
        'sponsorships': sponsorships,
        'amount_earned': amount_earned,
        'challenges_recieved': challenges_recieved,
        'own_page': own_page,
        'person': person,
        'tab_name': 'raised',
    }
    return render(request, 'profile/user_raised.html', context)


def user_donated(request, user_id=None):
    person = get_object_or_404(get_user_model(), pk=user_id)
    sponsorships_given = person.sponsorships_given.all()

    total_amount = 0
    total_amount_donated = 0
    for sponsorship in sponsorships_given:
        total_amount += sponsorship.total_amount
        total_amount_donated += sponsorship.amount_paid
    total_amount_owed = total_amount - total_amount_donated

    challenges_given = person.challenges_given.all().order_by('end_date')
    own_page = request.user.id == person.id

    context = {
        'sponsorships_given': sponsorships_given,
        'total_amount': total_amount,
        'total_amount_donated': total_amount_donated,
        'total_amount_owed': total_amount_owed,
        'challenges_given': challenges_given,
        'own_page': own_page,
        'person': person,
        'tab_name': 'donations',
    }
    return render(request, 'profile/user_donated.html', context)


def signup_or_login(request):
    redirect_to = request.GET.get(REDIRECT_FIELD_NAME,
                                  request.POST.get(REDIRECT_FIELD_NAME, ''))
    if redirect_to:
        if not is_safe_url(url=redirect_to, host=request.get_host()):
            redirect_to = ''

    if request.user.is_authenticated():
        if redirect_to:
            return HttpResponseRedirect(redirect_to)
        return redirect('profile:my_page')

    context = {
        'redirect_field_name': REDIRECT_FIELD_NAME,
        'redirect_field_value': redirect_to,
        'form': LoginForm,
        'signup_form': SignupForm
    }
    return render(request, 'profile/signup_or_login.html', context)


@login_required
def sign_in_landing(request):
    user = request.user

    if user.newsletter and settings.COURRIERS_MAILCHIMP_API_KEY:
        try:
            m = mailchimp.Mailchimp(settings.COURRIERS_MAILCHIMP_API_KEY)
            m.lists.subscribe(settings.COURRIERS_MAILCHIMP_LIST,
                              {'email': user.email})
            user.newsletter = False
            user.save()
            messages.success(
                request,  _("The email has been successfully subscribed"))
        except mailchimp.ListAlreadySubscribedError:
            messages.error(
                request,  _("That email is already subscribed to the list"))
            return HttpResponseRedirect('/')
        except mailchimp.Error as e:
            log.error("mailchimp error: %s, %s", e.__class__, e)
            messages.error(request,  _("An error occurred while subscribing"
                                       " to mailing list."))
            return HttpResponseRedirect('/')

    if not user.greeted:
        user.greeted = True
        user.save()
        url = reverse('profile:credit_card_prompt')
        return HttpResponseRedirect(url)

    redirect_to = request.GET.get(REDIRECT_FIELD_NAME, '')
    if redirect_to:
        if is_safe_url(url=redirect_to, host=request.get_host()):
            return HttpResponseRedirect(redirect_to)
    return redirect('profile:my_page')


@login_required
def credit_card_prompt(request):
    ctx = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'email': request.user.email
    }
    return render(request, 'profile/credit_card_prompt.html', ctx)


@login_required
@csrf_exempt
def register_customer(request):
    token = request.POST['stripeToken']
    stripe.api_key = settings.STRIPE_SECRET_KEY
    customer = stripe.Customer.create(source=token,
                                      description=request.user.username,
                                      email=request.user.email)
    request.user.stripe_customer_id = customer.id
    request.user.save()
    messages.success(request, _("Thank you! Your card has been successfully registered with Masanga Runners."))
    return redirect('profile:user_settings')


@login_required
def unsubscribe(request):
    user = request.user
    user.subscribed = False
    user.save()
    return render(request, 'profile/unsubscribed_success.html', {})


@login_required
def subscribe(request):
    user = request.user
    user.subscribed = True
    user.save()
    return render(request, 'profile/subscribed_success.html', {})


@login_required
def unregister_card(request):
    user = request.user
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        scu = stripe.Customer.retrieve(user.stripe_customer_id)
        scu.delete()
        user.stripe_customer_id = None
        user.save()
    except Exception as exc:
        raise
    messages.success(request, _("You have successfully deregistered your card."))
    return redirect('profile:user_settings')


@login_required
def user_settings(request):
    if request.user and request.user.is_authenticated():
        user = User.objects.get(pk=request.user.pk)
    else:
        user = None

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST, instance=user)
        if user_profile_form.is_valid():
            user_profile_form.save()
            # Let's redirect as the username may have changed
            return HttpResponseRedirect(reverse('profile:user_settings'))
    else:
        user_profile_form = UserProfileForm(instance=user)

    ctx = {
        'user_profile_form': user_profile_form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'profile/user_settings.html', ctx)


@login_required
def my_page(request):
    url = reverse('profile:overview', kwargs={'user_id': request.user.id})
    return HttpResponseRedirect(url)


@login_required
def make_profile_public(request):
    request.user.is_public = True
    request.user.save()
    messages.info(request, _("Your settings has been saved."))
    return redirect('profile:user_settings')


@login_required
def make_profile_private(request):
    request.user.is_public = False
    request.user.save()
    messages.info(request, _("Your settings has been saved."))
    return redirect('profile:user_settings')
