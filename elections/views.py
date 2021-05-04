from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import Bill

# Create your views here.

class AboutView(generic.TemplateView):
    template_name = 'elections/about.html'


# Bill-related views

class BillListView(generic.ListView):
    model = Bill
    queryset = Bill.objects.filter(state=Bill.OPEN)

class BillProposalsView(LoginRequiredMixin, generic.ListView):
    model = Bill
    raise_exception = True

    def get_queryset(self):
        return self.request.user.bill_set.all()

class BillVotesView(LoginRequiredMixin, generic.ListView):
    model = Bill
    raise_exception = True

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
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    bill = Bill.objects.get(pk=pk)
    if bill.state != Bill.OPEN:
        return HttpResponseForbidden()

    vote = request.POST.get('vote')
    if not vote:
        return HttpResponseBadRequest()

    if vote == 'vote-yes':
        bill.vote(True, request.user)
    elif vote == 'vote-no':
        bill.vote(False, request.user)
    else:
        return HttpResponseBadRequest()

    return JsonResponse({
        'yes-votes': bill.yes_votes.count(),
        'no-votes': bill.no_votes.count(),
    })



def context_repo(request):
    return {'github_repo': settings.ELECTIONS_REPO}
