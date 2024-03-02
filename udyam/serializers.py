# serializers.py
from rest_framework import serializers
from .models import Team, Event
from members.models import User

class TeamCreateSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(write_only=True)
    leader_email = serializers.EmailField(write_only=True)

    class Meta:
        model = Team
        fields = ['event_name', 'team_name', 'leader_email']
    
    def validate(self, data):
        event_name = data.pop('event_name', None)
        event = self.get_event_instance_by_name(event_name)
        data['event'] = event
        return data
    
    def create(self, validated_data):
        # Remove email fields from validated_data
        leader_email = validated_data.pop('leader_email', None)

        # Get or create the User instances based on the email fields
        leader = self.get_user_instance_by_email(leader_email)

        # Create the Team instance without the email fields
        team = Team.objects.create(leader=leader, **validated_data)

        return team
    
    def get_event_instance_by_name(self, name):
        try:
            return Event.objects.get(name=name)
        except Event.DoesNotExist:
            raise serializers.ValidationError(f"Event with name '{name}' does not exist.")

    def get_user_instance_by_email(self, email):
        # Ensure that you correctly obtain or create the User instance based on the email
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with email '{email}' does not exist.")


class TeamSerializer(serializers.ModelSerializer):
    event_name = serializers.ReadOnlyField(source='event.name')
    leader_email = serializers.EmailField(source='leader.email')
    member1_email = serializers.EmailField(source='member1.email')
    member2_email = serializers.EmailField(source='member2.email')

    class Meta:
        model = Team
        fields = ['event_name', 'team_name', 'leader_email', 'member1_email', 'member2_email']


class TeamCountSerializer(serializers.ModelSerializer):
    team_count = serializers.IntegerField()

    class Meta:
        model = Event
        fields = ['name', 'team_count']