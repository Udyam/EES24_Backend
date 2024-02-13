from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Team, Event
from .serializers import TeamCreateSerializer, TeamCountSerializer
from members.models import User


class TeamCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract relevant data from the request
        event_name = request.data.get('event_name')
        team_name = request.data.get('team_name')
        leader_email = request.data.get('leader_email')
        member1_email = request.data.get('member1_email')
        member2_email = request.data.get('member2_email')

        # Validate event existence
        try:
            event = Event.objects.get(name=event_name)
        except Event.DoesNotExist:
            return Response({"error": f"Event with name '{event_name}' does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate email addresses and convert to User instances
        leader = self.get_user_instance_by_email(leader_email)
        member1 = self.get_user_instance_by_email(member1_email)
        member2 = self.get_user_instance_by_email(member2_email)

        if leader is not None:
            if not leader.is_verified:
                return Response({"error": "Leader not verified."},status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"Error" : "Leader should be provided."},status=status.HTTP_400_BAD_REQUEST)

        if member1 is not None:
            if not member1.is_verified:
                return Response({"error": "Member1 not verified."},status=status.HTTP_400_BAD_REQUEST)

        if member2 is not None:
            if not member2.is_verified:
                return Response({"error" : "Member2 not verified."},status=status.HTTP_400_BAD_REQUEST)

        # Validate that team name is unique for the event
        if Team.objects.filter(event=event, team_name=team_name).exists():
            return Response({"error": "Team name must be unique for the event."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that each user is part of only one team for the event
        if self.user_is_part_of_team(leader, event) or \
                self.user_is_part_of_team(member1, event) or \
                self.user_is_part_of_team(member2, event):
            return Response({"error": "User is already part of a team for this event."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate that the requesting user is part of the team
        requesting_user = request.user
        if requesting_user not in [leader, member1, member2]:
            return Response({"error": "You can only register a team if you are a part of the team."},
                            status=status.HTTP_403_FORBIDDEN)

        # Continue with the creation logic if all checks pass
        serializer = TeamCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("You Have registered Successfully", status=status.HTTP_201_CREATED)

    def get_user_instance_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def user_is_part_of_team(self, user, event):
        return Team.objects.filter(event=event, leader=user).exists() or \
            Team.objects.filter(event=event, member1=user).exists() or \
            Team.objects.filter(event=event, member2=user).exists()


class TeamCountAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Query to get the count of teams for each event
        event_counts = Event.objects.annotate(team_count=Count('teams'))

        # Serialize the data
        serializer = TeamCountSerializer(event_counts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



