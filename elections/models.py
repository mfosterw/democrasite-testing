from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

class Bill(models.Model):
    # Display info
    name = models.CharField(max_length = 100)
    description = models.TextField()
    # Github info
    pr_num = models.IntegerField('pull request')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    additions = models.IntegerField()
    deletions = models.IntegerField()
    sha = models.CharField(max_length=40) # Unique sha of PR commit
    # Backend info
    OPEN = 'o'
    APPROVED = 'a'
    REJECTED = 'r'
    FAILED = 'f' # Failed to reach quorum
    CLOSED = 'c' # PR closed on Github
    STATES = (
        (OPEN, 'Open'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (FAILED, 'Not Enough Votes'),
        (CLOSED, 'PR Closed'),
    )
    state = models.CharField(max_length=1, choices=STATES, default=OPEN)
    constitutional = models.BooleanField(default=False,
        help_text='This is true only for amendments to the constitution')

    # Automatic fields
    prop_date = models.DateTimeField('date proposed', auto_now_add=True)
    yes_votes = models.ManyToManyField(User, related_name='yes_votes', blank=True)
    no_votes = models.ManyToManyField(User, related_name='no_votes', blank=True)

    def __str__(self):
        return f'{self.name} (PR #{self.pr_num})'

    def get_absolute_url(self):
        '''Returns URL to view this Bill instance'''
        return reverse('elections:bill-detail', args=(self.id,))

    def vote(self, support, user):
        '''Sets the given user's vote based on the support parameter

        If the user already voted the way the method would set, their vote is
        removed from the bill (i.e. if user is in bill.yes_votes and support is
        True, user is removed from bill.yes_votes)
        '''
        if support:
            self.no_votes.remove(user)
            if self in user.yes_votes.all():
                self.yes_votes.remove(user)
            else:
                self.yes_votes.add(user)
        else:
            self.yes_votes.remove(user)
            if self in user.no_votes.all():
                self.no_votes.remove(user)
            else:
                self.no_votes.add(user)
