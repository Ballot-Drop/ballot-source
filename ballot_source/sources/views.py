from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from .models import Source, SourceDetail


class SourceListView(LoginRequiredMixin, ListView):
    model = Source


class SourceDetailView(LoginRequiredMixin, DetailView):
    model = Source
    ordering = ["-last_checked"]


class DiffView(LoginRequiredMixin, DetailView):
    model = SourceDetail
    context_object_name = "diff"
    template_name = "sources/diff_detail.html"
