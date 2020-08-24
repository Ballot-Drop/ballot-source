from django.urls import path

# from django.views.generic import TemplateView
from .views import SourceDetailView, SourceListView

app_name = "sources"
urlpatterns = [
    path("", SourceListView.as_view(), name="index"),
    path("<int:pk>", SourceDetailView.as_view(), name="detail"),
]
