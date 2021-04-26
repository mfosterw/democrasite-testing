import hmac
import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User

from .tasks import process_pull


# Code in this module is adapted from
# https://simpleisbetterthancomplex.com/tutorial/2016/10/31/how-to-handle-github-webhooks-using-django.html
@require_POST
@csrf_exempt
def github_hook(request):
    # Verify the request signature
    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden('Invalid signature')

    sha_name, signature = header_signature.split('=')
    mac = hmac.new(force_bytes(settings.ELECTIONS_GITHUB_WEBHOOK_SECRET),
        force_bytes(request.body), 'sha1')
    sig_valid = hmac.compare_digest(force_bytes(mac.hexdigest()),
        force_bytes(signature))
    if not (sha_name == 'sha1' and sig_valid):
        return HttpResponseForbidden('Invalid signature')

    # Process the GitHub event
    # For info on the GitHub Webhook API, go to
    # https://docs.github.com/en/developers/webhooks-and-events/webhook-events-and-payloads
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')
    payload = json.loads(request.POST['payload'])

    if event == 'ping':
        userinfo = json.loads(request.POST['payload'])['sender']
        user = User.objects.filter(social_auth__provider='github')\
            .get(social_auth__uid=userinfo['id'])
        return HttpResponse(f'{user.username} (id={user.id}, ' +
            f'id={userinfo["id"]}) is my favorite user')
    elif event == 'pull_request':
        process_pull.delay(payload['action'], payload['pull_request'])
        return HttpResponse('success')

    # In case we receive an event that's not ping or push
    return HttpResponse(status=204)
