from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView

from .forms import SourceForm
from .models import Source, SourceDetail


class SourceListView(LoginRequiredMixin, ListView):
    model = Source


class SourceDetailView(LoginRequiredMixin, DetailView):
    model = Source
    ordering = ["-last_checked"]


class SourceNewView(LoginRequiredMixin, FormView):
    form_class = SourceForm
    template_name = "sources/source_create.html"
    success_url = reverse_lazy("sources:detail")

    def form_valid(self, form):
        source = form.save()
        self.pk = source.pk
        return super(SourceNewView, self).form_valid(form)

    def get_success_url(self):
        return reverse("sources:detail", kwargs={"pk": self.pk})


class DiffView(LoginRequiredMixin, DetailView):
    model = SourceDetail
    context_object_name = "diff"
    template_name = "sources/diff_detail.html"
