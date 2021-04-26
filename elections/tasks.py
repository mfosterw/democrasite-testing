import requests
from datetime import timedelta
from requests_oauthlib import OAuth2

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger
from github import Github

from .models import Bill
from . import constitution

logger = get_task_logger(__name__)


@shared_task
def process_pull(action, pr):
    if action in ('opened', 'reopened'):
        try:
            author = User.objects.filter(social_auth__provider='github')\
                .get(social_auth__uid=pr['user']['id'])
        except User.DoesNotExist:
            # If the creator of the pull request does not have a linked account,
            # a Bill cannot be created and the pr is ignored.
            logger.info(f'PR {pr["number"]}: No bill created (user does not exist)')
            return

        diff = requests.get(pr['diff_url']).text
        constitutional = constitution.is_constitutional(diff)

        bill = Bill(
            name=pr['title'],
            description=pr['body'],
            pr_num=pr['number'],
            author=author,
            additions=pr['additions'],
            deletions=pr['deletions'],
            sha=pr['head']['sha'],
            active=True,
            constitutional=bool(constitutional),
        )
        bill.save()

        voting_ends = (timezone.now() +
            timedelta(days=settings.ELECTIONS_VOTING_PERIOD))
        # Pass id rather than bill object to avoid potential issues with
        # database refresh
        submit_bill.apply_async((bill.id,), eta=voting_ends)
        logger.info(f'PR {pr["number"]}: Bill {bill.id} created')
        return

    # Disable bill if pr is closed
    if action == 'closed':
        try:
            bill = Bill.objects.filter(pr_num=pr['number'])\
                .get(active=True)
        except Bill.DoesNotExist:
            logger.info(f'PR {pr["number"]}: No modification (no active bill)')
            return
        bill.active = False
        bill.save()
        logger.info(f'PR {pr["number"]}: Bill {bill.id} set to inactive')
        return

    logger.info(f'PR {pr["number"]}: Action not handled')
    return


@shared_task
def submit_bill(bill_id):
    bill = Bill.objects.get(pk=bill_id)
    if bill.active == False:
        logger.info(f'PR {bill.pr_num}: bill {bill.id} rejected as inactive')
        return

    ayes = bill.yes_votes.count()
    nays = bill.no_votes.count()
    total_votes = ayes + nays
    if total_votes < settings.ELECTIONS_MINIMUM_QUORUM:
        bill.active = False
        bill.save()
        logger.info((f'PR {bill.pr_num}: bill {bill.id} rejected with '
            'insufficient votes'))
        return

    approval = ayes / (total_votes)
    if bill.constitutional:
        approved = approval > settings.ELECTIONS_SUPERMAJORITY
    else:
        approved = approval > settings.ELECTIONS_NORMAL_MAJORITY

    if approved:
        msg = f''
        logger.info((f'PR {bill.pr_num}: Pull request passed with '
            f'{approval * 100}% of votes'))
        gh = Github(settings.ELECTIONS_GITHUB_TOKEN)
        repo = gh.get_repo(settings.ELECTIONS_REPO)
        pull = repo.get_pull(bill.pr_num)
        res = pull.merge(commit_message=msg + ' on Democrasite', sha=bill.sha)
        logger.info(f'PR {bill.pr_num} merged: {res.merged}')

        # Automatically update constitution line numbers if necessary
        if not bill.constitutional:
            diff = requests.get(pull.diff_url).text
            con_update = constitution.update_constitution(diff)
            if con_update:
                con_sha = repo.get_contents('elections/constitution.json').sha
                con_res = repo.update_file('elections/constitution.json',
                    message=f'Update Constitution for PR {bill.pr_num}',
                    content=con_update, sha=con_sha)
                logger.info(f'PR {bill.pr_num}: constitution updated')

    else:
        logger.info((f'PR {bill.pr_num}: Pull request failed with {approval}%'
            ' of votes'))

    bill.active = False
    bill.save()
