# urls.py
from django.urls import path, include
from .views import TeamCreateAPIView, TeamCountAPIView, TeamInviteAPIView, TeamJoinAPIView, TeamAPIView, TeamDeleteAPIView

urlpatterns = [
    path('teams/create/', TeamCreateAPIView.as_view(), name='create-team'),
    path('teams/invite/', TeamInviteAPIView.as_view(), name='team-invite'),
    path('teams/join', TeamJoinAPIView.as_view(), name='team-join'),
    path('teams/', TeamAPIView.as_view(), name='team-view'),
    path('teams/delete/', TeamDeleteAPIView.as_view(), name='team-delete'),
    path('teams/count/', TeamCountAPIView.as_view(), name='team-count'),
]
