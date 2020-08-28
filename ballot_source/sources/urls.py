from django.urls import path

# from django.views.generic import TemplateView
from .views import DiffView, SourceDetailView, SourceListView, SourceNewView

app_name = "sources"
urlpatterns = [
    path("", SourceListView.as_view(), name="index"),
    path("<int:pk>", SourceDetailView.as_view(), name="detail"),
    path("new", SourceNewView.as_view(), name="new"),
    path("<int:source_pk>/<int:pk>", DiffView.as_view(), name="diff"),
]
