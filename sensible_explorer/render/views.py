from django.shortcuts import render_to_response
from django.template import RequestContext
from django_sensible import oauth2
from django_sensible import SECURE_CONFIG
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def refresh_token(user):
	print 'User authenticated: ', user.is_authenticated()
	token_loc = ''
	if user.is_authenticated():
		token_loc = oauth2.getToken(user, 'connector_raw.all_data')
		oauth2.query(settings.SERVICE_URL + 'connectors/connector_raw/v1/location/', token_loc, '&dummy=True&decrypted=True', SECURE_CONFIG.CLIENT_ID, SECURE_CONFIG.CLIENT_SECRET, settings.APPLICATION_URL[-1]+reverse('grant'), settings.SERVICE_REFRESH_TOKEN_URL)
		token_loc = oauth2.getToken(user, 'connector_raw.all_data')
	return token_loc


def mymovements(request):
	token_loc = refresh_token(request.user)
	if token_loc == '':
		return HttpResponseRedirect(reverse('login'))
	return render_to_response('mymovements.html', {'token_loc': token_loc, 'SERVICE_URL': settings.SERVICE_URL}, 
		context_instance=RequestContext(request))
