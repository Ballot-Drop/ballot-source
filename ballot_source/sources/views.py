from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from .forms import SourceForm
from .models import Source, SourceDetail


class SourceListView(LoginRequiredMixin, ListView):
    model = Source


class SourceDetailView(LoginRequiredMixin, DetailView):
    model = Source
    ordering = ["-last_checked"]


class SourceFormView(LoginRequiredMixin, FormView):
    form_class = SourceForm
    template_name = "sources/source_create.html"
    success_url = reverse_lazy("sources:detail")

    def form_valid(self, form):
        source = form.save()
        self.pk = source.pk
        self.add_another = True if form.data.get("add_another", False) else False
        return super(SourceFormView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        if self.add_another:
            return reverse("sources:new")
        return reverse("sources:detail", kwargs={"pk": self.pk})


class SourceEditView(LoginRequiredMixin, UpdateView):
    form_class = SourceForm
    template_name = "sources/source_create.html"

    def get_object(self, queryset=None):
        obj = Source.objects.get(pk=self.kwargs["pk"])
        return obj


class ManageSubscriptions(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        """
        Overrides http method using action from data
        """
        self.json_response = {"source_pk": None, "status": None, "action": None}

        try:
            if request.method == "GET":
                self.source = Source.objects.get(pk=request.GET.get("pk", None))
            else:
                self.source = Source.objects.get(pk=request.POST.get("pk", None))
        except Source.DoesNotExist:
            self.json_response["status"] = "Source matching pk does not exist"
            return JsonResponse(self.json_response)
        self.json_response["source_pk"] = self.source.pk

        if request.method == "GET":
            self.json_response["action"] = request.method
            return super(ManageSubscriptions, self).dispatch(request, *args, **kwargs)

        request.method = request.POST.get("action", "POST").upper()
        self.json_response["action"] = request.method

        return super(ManageSubscriptions, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.json_response["status"] = (
            request.user in self.source.user_subscription.all()
        )
        return JsonResponse(self.json_response)

    def post(self, request, *args, **kwargs):
        if request.user not in self.source.user_subscription.all():
            self.source.user_subscription.add(request.user)
            self.json_response["status"] = "subscribed"
        else:
            self.json_response["status"] = "already subscribed"
        return JsonResponse(self.json_response)

    def delete(self, request, *args, **kwargs):
        if request.user not in self.source.user_subscription.all():
            self.json_response["status"] = "user is not subscribed"
        else:
            self.source.user_subscription.remove(request.user)
            self.json_response["status"] = "unsubscribed"
        return JsonResponse(self.json_response)


class DiffView(LoginRequiredMixin, DetailView):
    model = SourceDetail
    context_object_name = "diff"
    template_name = "sources/diff_detail.html"


class ScrapeView(LoginRequiredMixin, TemplateView):
    template_name = "sources/scrape.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context.get("pk", None):
            source = Source.objects.get(pk=context.get("pk"))
            context["source"] = source
            source.scrape()
            if source.details.first().date_pulled == source.last_checked:
                context["changes"] = [source]
        else:
            changes = []
            for source in Source.objects.all():
                # self.stdout.write(self.style.NOTICE(f"Scraping {source}"))
                source.scrape()
                # msg = "Success: No differences found"

                if source.details.first().date_pulled == source.last_checked:
                    # msg = "Success: Differences found"
                    changes.append(source)

            context["changes"] = changes
        return context


class SubscriptionList(LoginRequiredMixin, ListView):
    model = Source
    template_name = "sources/subscription_list.html"
    context_object_name = "sources"

    def get_queryset(self):
        queryset = super(SubscriptionList, self).get_queryset()
        queryset = queryset.filter(user_subscription__in=[self.request.user])
        return queryset
