from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import Bill

# Create your views here.

class AboutView(generic.TemplateView):
    template_name = 'elections/about.html'


class BillListView(generic.ListView):
    model = Bill
    queryset = Bill.objects.filter(active=True)

class BillProposalsView(generic.ListView):
    model = Bill

    def get_queryset(self):
        return self.request.user.bill_set.all()

class BillVotesView(generic.ListView):
    model = Bill

    def get_queryset(self):
        return (self.request.user.yes_votes.all() |
            self.request.user.no_votes.all())

class BillDetailView(generic.DetailView):
    model = Bill

class BillUpdateView(UserPassesTestMixin, generic.edit.UpdateView):
    model = Bill
    fields = ('name', 'description',)

    def test_func(self):
        return self.get_object().author == self.request.user


@require_POST
def vote(request, pk):
    if request.user.is_authenticated:
        bill = Bill.objects.get(pk=pk)
        vote = request.POST.get('vote')

        if vote:
            if vote == 'vote-yes':
                if bill in request.user.yes_votes.all():
                    bill.yes_votes.remove(request.user)
                else:
                    bill.no_votes.remove(request.user)
                    bill.yes_votes.add(request.user)
            elif vote == 'vote-no':
                if bill in request.user.no_votes.all():
                    bill.no_votes.remove(request.user)
                else:
                    bill.yes_votes.remove(request.user)
                    bill.no_votes.add(request.user)
            else:
                return HttpResponseBadRequest()

            return JsonResponse({
                'yes-votes': bill.yes_votes.count(),
                'no-votes': bill.no_votes.count(),
            })

        return HttpResponseBadRequest()

    return HttpResponseForbidden()


def context_repo(request):
    return {'github_repo': settings.ELECTIONS_REPO}
