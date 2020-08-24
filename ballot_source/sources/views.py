# from django.shortcuts import render
# from django.http import HttpResponse
# from django.views import View
from django.views.generic import DetailView, ListView

from .models import Source  # , SourceDetail


class SourceListView(ListView):
    model = Source


class SourceDetailView(DetailView):
    model = Source
