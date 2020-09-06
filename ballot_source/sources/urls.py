from django.urls import path

# from django.views.generic import TemplateView
from .views import (
    DiffView,
    ManageSubscriptions,
    ScrapeView,
    SourceDetailView,
    SourceEditView,
    SourceFormView,
    SourceListView,
    SubscriptionList,
)

app_name = "sources"
urlpatterns = [
    path("", SourceListView.as_view(), name="index"),
    path("<int:pk>", SourceDetailView.as_view(), name="detail"),
    path("subscribe", ManageSubscriptions.as_view(), name="subscribe"),
    path("new", SourceFormView.as_view(), name="new"),
    path("<int:pk>/edit", SourceEditView.as_view(), name="edit"),
    path("<int:source_pk>/<int:pk>", DiffView.as_view(), name="diff"),
    path("scrape/<int:pk>", ScrapeView.as_view(), name="scrape"),
    path("scrape", ScrapeView.as_view(), name="scrape"),
    path("subscriptions", SubscriptionList.as_view(), name="subscriptions"),
]
