"""democrasite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

See also democrasite/urls.py
"""

from django.urls import path

from . import views
from .webhooks import github_hook

app_name = 'elections'
urlpatterns = [
    path('', views.BillListView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('bill/<int:pk>/', views.BillDetailView.as_view(), name='bill-detail'),
    path('bill/<int:pk>/edit', views.BillUpdateView.as_view(), name='bill-edit'),
    path('bill/<int:pk>/vote', views.vote, name='bill-vote'),
    path('proposals/', views.BillProposalsView.as_view(), name='my-bills'),
    path('votes/', views.BillVotesView.as_view(), name='my-bill-votes'),
    path('webhook/github/', github_hook),
]
