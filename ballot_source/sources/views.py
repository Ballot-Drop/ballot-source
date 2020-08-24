# from django.shortcuts import render
# from django.http import HttpResponse
# from django.views import View
from django.views.generic import DetailView, ListView

from .models import Source, SourceDetail


class SourceListView(ListView):
    model = Source
    # todo: order by date desc


class SourceDetailView(DetailView):
    model = Source


class DiffView(DetailView):
    model = SourceDetail
    context_object_name = "diff"
    template_name = "sources/diff_detail.html"
