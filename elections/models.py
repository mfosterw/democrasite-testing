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
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    additions = models.IntegerField()
    deletions = models.IntegerField()
    sha = models.CharField(max_length = 40) # Unique sha of PR commit
    # Backend info
    active = models.BooleanField(default=True)
    constitutional = models.BooleanField(default=False,
        help_text='This is true only for amendments to the constitution')

    # Automatic fields
    prop_date = models.DateTimeField('date proposed', auto_now_add=True)
    yes_votes = models.ManyToManyField(User, related_name='yes_votes', blank=True)
    no_votes = models.ManyToManyField(User, related_name='no_votes', blank=True)

    def __str__(self):
        return f'{self.name} (PR #{self.pr_num})'

    def get_absolute_url(self):
        '''Returns URL to view this Course instance'''
        return reverse('elections:bill-detail', args=(self.id,))
