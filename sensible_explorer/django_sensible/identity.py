import json
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
import SECURE_CONFIG
import oauth2
from .models import *


@login_required
def requestAttributes(request):
    url = settings.IDP_AUTHORIZATION_URL
    url += "redirect_uri="+settings.IDP_MY_REDIRECT
    url += "&client_id="+SECURE_CONFIG.IDP_CLIENT_ID
    url += "&response_type=code"
    try:
        url += "&scope="+','.join([s.scope for s in Scope.objects.filter(type=Type.objects.get(type='identity'))])
    except Type.DoesNotExist: return redirect('home')
    state = oauth2.generateState(request.user)
    url += '&state='+state
    return redirect(url)
    #return HttpResponse(url)

@login_required
def attributesRedirect(request):
    token = oauth2.exchangeCodeForToken(request, SECURE_CONFIG.IDP_CLIENT_ID, SECURE_CONFIG.IDP_CLIENT_SECRET, settings.IDP_MY_REDIRECT, settings.IDP_URL+'oauth2/oauth2/token/?')
    if 'error' in token:
        return redirect('home')
    oauth2.saveToken(request.user, token)
    getAttributes(request.user, ['first_name'])
    return redirect('home')

@login_required
def test(request):
    return HttpResponse(json.dumps({"user": request.user.username}))


def getAttributes(user, attributes):
    tokens = set()
    for attribute in attributes:
        try:
            scope = (Attribute.objects.get(attribute=attribute).scope)
        except Attribute.DoesNotExist: continue
        token = oauth2.getToken(user, scope)
        tokens.add(token)
    if len(tokens) > 1:
        return json.dumps({'error':'need multiple queries'})
    if len(tokens) == 0:
        return json.dumps({'error':'no token available'})

    response = oauth2.query(settings.IDP_URL + 'openid/attributes/', list(tokens)[0], '&attributes='+','.join(attributes), SECURE_CONFIG.IDP_CLIENT_ID, SECURE_CONFIG.IDP_CLIENT_SECRET, settings.IDP_MY_REDIRECT, settings.IDP_URL+'oauth2/oauth2/token/?' )
    for attribute in response:
        try:
            s = 'user.'+attribute + '= response["%s"]'%attribute
            exec(s)
        except eval(attribute.split('.')[0].capitalize()).DoesNotExist: eval(attribute.split('.')[0].capitalize()).objects.create(user = user, student_id = response[attribute])
        except: continue
    user.save()
    return json.dumps(response)
