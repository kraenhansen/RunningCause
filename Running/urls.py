from django.conf.urls import patterns, url, include
from Running import views
from django.conf import settings

urlpatterns = patterns('',
    (r'^account/logout/$', 'django.contrib.auth.views.logout',
                          {'next_page': '/'}),
    (r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^account/', include('allauth.urls')),
    url(r'^my_page/$', views.my_page, name='my_page'),
    url(r'^(?P<user_id>\S+)/profile/$', views.user, name='user'),
    url(r'^(?P<runner_id>\S+)/input_run/$', views.input_run, name='input'),
    url(r'^(?P<run_id>\S+)/edit_run/$', views.edit_run, name='edit'),
    url(r'^(?P<sponsee_id>\S+)/sponsor/$', views.sponsor, name='sponsor'),
    url(r'^(?P<sponsee_id>\S+)/make_wager/$', views.wager, name='wager'),
    url(r'^(?P<wager_id>\S+)/update_wager/$', views.update_wager, name='update_wager'),
    url(r'^(?P<wager_id>\S+)/confirm_wager/$', views.confirm_wager, name='confirm_wager'),
    url(r'^(?P<wager_id>\S+)/decline_wager/$', views.decline_wager, name='decline_wager'),
    url(r'^(?P<sponsee_id>\S+)/sponsor/(?P<sponsorship_id>\S+)/$', views.sponsor, name='sponsor_from_invite'),
    url(r'^(?P<sponsee_id>\S+)/make_wager/(?P<wager_id>\S+)/$', views.wager, name='wager_from_invite'),
    url(r'^(?P<sponsor_id>\S+)/invite/$', views.invite_sponsor, name='invite_sponsor'),
    url(r'^(?P<sponsor_id>\S+)/invite_wager/$', views.invite_wager, name='invite_wager'),
    url(r'^invite_from_email/$', views.invite_sponsor, name='invite_from_email'),
    url(r'^(?P<runner_id>\S+)/register/runkeeper/$', views.register_runkeeper, name='register_runkeeper'),
    url(r'^(?P<sponsorship_id>\S+)/endsponsorship/(?P<runner_id>\S+)/$', views.end_sponsorship, name='end_sponsorship'),
    url(r'^(?P<user_id>\S+)/makeuserpublic/$', views.make_user_public, name='make_user_public'),
    url(r'^(?P<user_id>\S+)/makeuserprivate/$', views.make_user_private, name='make_user_private'),
    url(r'^register_customer/$', views.register_customer, name='register_customer'),
    url(r'^overview/$', views.overview, name='overview'),
    url(r'^unsubscribe/$', views.unsubscribe, name='unsubscribe'),
    url(r'^signuporlogin/$', views.signup_or_login, name='signup_or_login'),
    url(r'^credit_card_prompt/$', views.credit_card_prompt, name='credit_card_prompt'),
    url(r'^sign_in_landing/$', views.sign_in_landing, name='sign_in_landing'),
    url(r'^$', views.home, name='home'),
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
        )