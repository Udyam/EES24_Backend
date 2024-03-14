from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Team, Event
from .serializers import TeamCreateSerializer, TeamCountSerializer, TeamSerializer
from members.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.http import QueryDict


class TeamCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_name = request.data.get('event_name')
        team_name = request.data.get('team_name')
        leader_email = request.data.get('leader_email')

        # checking if event exists
        try:
            event = Event.objects.get(name=event_name)
        except Event.DoesNotExist:
            return Response({"error": f"Event with name '{event_name}' does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # getting leader instance
        leader = self.get_user_instance_by_email(leader_email)

        #checking if leader is verified
        if leader is not None:
            if not leader.is_verified:
                return Response({"error": "Leader not verified."},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error" : "Leader should be provided."},status=status.HTTP_400_BAD_REQUEST)
        
        # checking if same team name exists in the event
        if Team.objects.filter(event=event, team_name=team_name).exists():
            return Response({"error": "Team name must be unique for the event."}, status=status.HTTP_400_BAD_REQUEST)

        # checking is user is part of a team already
        if self.user_is_part_of_team(leader, event):
            return Response({"error": "User is already part of a team for this event."},status=status.HTTP_400_BAD_REQUEST)
        
        # checking if the user posting the request is the leader of the team
        requesting_user = request.user
        if requesting_user != leader:
            return Response({"error": "You can only register a team if you are a part of the team."},
                            status=status.HTTP_403_FORBIDDEN)
        
        # creating the team in the database
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
        

class TeamInviteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_name = request.data.get('event_name')
        team_name = request.data.get('team_name')
        leader_email = request.data.get('leader_email')
        member_email = request.data.get('member_email')
        
        # checking if event exists
        try:
            event = Event.objects.get(name=event_name)
        except Event.DoesNotExist:
            return Response({"error": f"Event with name '{event_name}' does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # getting respective leader, member and team instances
        leader = self.get_user_instance_by_email(leader_email)
        member = self.get_user_instance_by_email(member_email)
        team = self.get_team_instance_by_team_name_and_event(team_name, event)

        # checking if the user posting the request is the leader (only leaders can invite)
        requesting_user = request.user
        if requesting_user != leader:
            return Response({"error": "You can only register a team if you are a part of the team."},
                            status=status.HTTP_403_FORBIDDEN)
        
        # checking if the user posting the request is the leader (only leaders can invite)
        if requesting_user != team.leader:
            return Response({"error" : "Only a leader can invite other members"}, status=status.HTTP_403_FORBIDDEN)
        
        #checking if the leader is verified
        if leader is not None:
            if not leader.is_verified:
                return Response({"error": "Leader not verified."},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error" : "Leader should be provided."},status=status.HTTP_400_BAD_REQUEST)
        
        # checking if the member is verified
        if member is not None:
            if not member.is_verified:
                return Response({"error": "Member not verified."},status=status.HTTP_400_BAD_REQUEST)
            if member == leader or requesting_user == member:
                return Response({"error" : "Invalid invitation"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error" : "Member should be provided."},status=status.HTTP_400_BAD_REQUEST)
        
        # checking if the team sending the invite exists
        if not Team.objects.filter(event=event, team_name=team_name).exists():
            return Response({"error": "Team must exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        # checking if the member user if part of a team already
        if self.user_is_part_of_team(member, event):
            return Response({"error": "User is already part of a team for this event."},status=status.HTTP_400_BAD_REQUEST)
        
        if event.name in ['digisim', 'ichip', 'commnet', 'xiota']:
            if team.member1 is not None:
                return Response({"error": "Team is full"}, status=status.HTTP_400_BAD_REQUEST)

        if team.member1 is not None and team.member2 is not None:
            return Response({"error": "Team is full"}, status=status.HTTP_400_BAD_REQUEST)
        
        # generating email link and sending the email
        link = self.generate_link(team_name, event_name, member_email)
        
        from_email = settings.EMAIL_HOST_USER
        send_mail("Team Invite", f"Here is the {link} to join {team_name} for the event {event_name}", from_email, (member_email,))

        return Response({'message': 'Email sent for Invitation.'}, status=status.HTTP_200_OK)
        
    
    def get_user_instance_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        
    def user_is_part_of_team(self, user, event):
        return Team.objects.filter(event=event, leader=user).exists() or \
            Team.objects.filter(event=event, member1=user).exists() or \
            Team.objects.filter(event=event, member2=user).exists()
    
    def get_team_instance_by_team_name_and_event(self, team_name, event):
        try:
            return Team.objects.filter(event=event,team_name=team_name).first()
        except Team.DoesNotExist:
            return None
        
    def generate_link(self, team_name, event_name, member_email):
        q = QueryDict({}, mutable=True)
        q["team_name"] = team_name
        q["event_name"] = event_name
        q["member_email"] = member_email
        # frontend url
        # join_link = "http://localhost:8000/udyam/teams/join?"
        join_link = "https://eesiitbhu.co.in/invite?"
        return join_link + q.urlencode()
        

class TeamJoinAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        team_name = request.GET.get("team_name")
        event_name = request.GET.get("event_name")
        member_email = request.GET.get("member_email")

        # checking if the event exists
        try:
            event = Event.objects.get(name=event_name)
        except Event.DoesNotExist:
            return Response({"error": f"Event with name '{event_name}' does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        # getting respective member and team instances
        member = self.get_user_instance_by_email(member_email)
        team = self.get_team_instance_by_team_name_and_event(team_name, event)

        # checking if the user making the get request is the member associated with the link
        requesting_user = request.user
        if requesting_user != member:
            return Response({"error": "You can only register a team if you are a part of the team."},
                            status=status.HTTP_403_FORBIDDEN)

        # checking if the member is verified
        if member is not None:
            if not member.is_verified:
                return Response({"error": "Member not verified."},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error" : "Member should be provided."},status=status.HTTP_400_BAD_REQUEST)
        
        # checking if the team exists
        if not Team.objects.filter(event=event, team_name=team_name).exists():
            return Response({"error": "Team must exist."}, status=status.HTTP_400_BAD_REQUEST)

        # checking if the member user is already part of another team
        if self.user_is_part_of_team(member, event):
            return Response({"error": "User is already part of a team for this event."},status=status.HTTP_400_BAD_REQUEST)
        
        # checking if the team is full
        if event.name in ['digisim', 'ichip', 'commnet', 'xiota']:
            if team.member1 is not None:
                return Response({"error": "Team is full"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                team.member1 = member

        else:
            if team.member1 is None:
                team.member1 = member
            elif team.member2 is None:
                team.member2 = member
            else:
                return Response({"error":"Team is full"})

        team.save()

        return Response({"message" : f"{member_email} successfully joined team"})

    def get_user_instance_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error" : "User does not exist"})
    
    def user_is_part_of_team(self, user, event):
        return Team.objects.filter(event=event, leader=user).exists() or \
            Team.objects.filter(event=event, member1=user).exists() or \
            Team.objects.filter(event=event, member2=user).exists()

    def get_team_instance_by_team_name_and_event(self, team_name, event):
        try:
            return Team.objects.filter(event=event,team_name=team_name).first()
        except Team.DoesNotExist:
            return Response({"error" : "Team does not exist"})


class TeamDeleteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        team_name = request.data.get("team_name")
        event_name = request.data.get("event_name")
        leader_email = request.data.get("leader_email")

        try:
            event = Event.objects.get(name=event_name)
        except Event.DoesNotExist:
            return Response({"error":"Event does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        leader = self.get_user_instance_by_email(leader_email)
        team = self.get_team_instance_by_team_name_and_event(team_name, event)

        requesting_user = request.user
        if requesting_user != leader:
            return Response({"error": "You can only delete a team if you are a team leader."},
                            status=status.HTTP_403_FORBIDDEN)
        
        if requesting_user != team.leader:
            return Response({"error" : "User is not the leader of this team"}, status=status.HTTP_403_FORBIDDEN)
        
        if leader is not None:
            if not leader.is_verified:
                return Response({"error": "Leader not verified."},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error" : "Leader should be provided."},status=status.HTTP_400_BAD_REQUEST)
        
        if not Team.objects.filter(event=event, team_name=team_name).exists():
            return Response({"error": "Team must exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        team.delete()

        return Response({"message" : f"Team {team_name} successfully deleted"}, status=status.HTTP_202_ACCEPTED)

    
    def get_team_instance_by_team_name_and_event(self, team_name, event):
        try:
            return Team.objects.filter(event=event,team_name=team_name).first()
        except Team.DoesNotExist:
            return Response({"error" : "Team does not exist"})
        
    def get_user_instance_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error" : "User does not exist"})
        

class TeamAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requesting_user = request.user
        result1 = Team.objects.filter(leader=requesting_user)
        result2 = Team.objects.filter(member1=requesting_user)
        result3 = Team.objects.filter(member2=requesting_user)
        result = result1 | result2 | result3
        serializer = TeamSerializer(result, many=True, context={'request' : request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamCountAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Query to get the count of teams for each event
        event_counts = Event.objects.annotate(team_count=Count('teams'))

        # Serialize the data
        serializer = TeamCountSerializer(event_counts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



