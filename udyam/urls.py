# urls.py
from django.urls import path, include
from .views import TeamCreateAPIView, TeamCountAPIView

urlpatterns = [
    path('create/team/', TeamCreateAPIView.as_view(), name='create-team'),
    path('teams/count/', TeamCountAPIView.as_view(), name='team-count'),
]
