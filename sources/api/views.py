from rest_framework import viewsets, serializers, status
from rest_framework.views import  APIView
from rest_framework.response import Response
from mci.models import *
from django.db.models import get_model


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person


class StaffMembershipSerializer(serializers.ModelSerializer):
    person = PersonSerializer(source='person')

    class Meta:
        model = StaffMembership


class PersonalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalData


class TraumaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trauma

class TraumaNestedViewSet(viewsets.ViewSet):
    model = Trauma

    def list(self, request, nested_1_pk=None):
        victim = Victim.objects.get(pk=nested_1_pk)
        traumas = victim.traumas.all()
        serializer = TraumaSerializer(traumas, many=True)

        return Response(serializer.data)

    def create(self, request, nested_1_pk):
        victim = Victim.objects.get(pk=nested_1_pk)
        try:
            trauma_type = request.DATA['trauma_type']
            bodypart = request.DATA['bodypart']
            ai_type = request.DATA['ai_type']
            ai_bodypart = request.DATA['ai_bodypart']
            description = request.DATA['description']
            agent = request.DATA['agent']
            timestamp = request.DATA['timestamp']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        trauma = Trauma()
        user = User.objects.get(pk=agent)
        trauma.victim = victim
        trauma.trauma_type = trauma_type
        trauma.bodypart = bodypart
        trauma.ai_type = ai_type
        trauma.ai_bodypart = ai_bodypart
        trauma.description =  description
        trauma.agent = user
        trauma.timestamp = timestamp
        trauma.save()
        serializer = TraumaSerializer(trauma)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class VictimSerializer(serializers.ModelSerializer):
    personal_data = PersonalDataSerializer(source='personal_data')

    class Meta:
        model = Victim


# Victims related to Incidents with url such as http://sitename/api/incidents/1/victims/
class VictimNestedViewSet(viewsets.ViewSet):
    model = Victim

    def list(self, request, nested_1_pk=None):

        tag_id = request.QUERY_PARAMS.get('tag_id', None)

        incident = Incident.objects.get(pk=nested_1_pk)
        if tag_id is None:
            victims = incident.victims.all()
        else:
            print "entrou"
            try:
                tag_id = long(tag_id)
            except ValueError:
                return Response([])

            victims = incident.victims.filter(tag_id=tag_id)
        serializer = VictimSerializer(victims, many=True)
        return Response(serializer.data)

    def create(self, request, nested_1_pk):
        victim = Victim()
        incident = Incident.objects.get(pk=nested_1_pk)
        victim.incident = incident
        pd = PersonalData()
        try:
            victim.creation_time = request.DATA['creation_time']
            victim.creation_agent = User.objects.get(pk=request.DATA['creation_agent'])
            victim.tag_id = request.DATA['tag_id']
            pd.victim_name = request.DATA['personal_data']['victim_name']
            pd.age = request.DATA['personal_data']['age']
            pd.gender = request.DATA['personal_data']['gender']
            pd.height = request.DATA['personal_data']['height']
            pd.weight = request.DATA['personal_data']['weight']
            pd.address = request.DATA['personal_data']['address']
            pd.phone_number = request.DATA['personal_data']['phone_number']
            pd.religion = request.DATA['personal_data']['religion']
            pd.comments = request.DATA['personal_data']['comments']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        pd.save()
        victim.personal_data = pd
        victim.save()
        return Response(data=VictimSerializer(victim).data, status=status.HTTP_201_CREATED)

    # TODO: find some way to remove GET from the options from url's like http://sitename/api/incidents/1/victims/2
    # TODO: this is better than returning a 403
    def retrieve(self):
        return Response(status=status.HTTP_403_FORBIDDEN)


class StaffMembershipNestedViewSet(viewsets.ViewSet):
    model = StaffMembership

    def list(self, nested_1_pk=None):
        staff = Staff.objects.get(pk=nested_1_pk)
        memberships = staff.memberships.all()
        serializer = StaffMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    def create(self, request, nested_1_pk):
        staff = Staff.objects.get(pk=nested_1_pk)
        try:
            person_id = request.DATA['person_id']
            role = request.DATA['role']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        person = Person.objects.get(pk=person_id)
        sm = StaffMembership()
        sm.person = person
        sm.staff = staff
        sm.role = role
        sm.save()
        serializer = StaffMembershipSerializer(sm)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'id')


class AuthenticateViewSet(viewsets.ViewSet):
    permission_classes = []

    def list(self, request):
        return Response({"success": True, "user_info": UserSerializer(request.api_user).data})

class PersonViewSet(viewsets.ModelViewSet):
    model = Person


class StaffViewSet(viewsets.ModelViewSet):
    model = Staff


class IncidentViewSet(viewsets.ModelViewSet):
    model = Incident


#TODO: forbid POST method
class VictimViewSet(viewsets.ModelViewSet):
    model = Victim
    serializer_class = VictimSerializer


class TraumaViewSet(viewsets.ModelViewSet):
    model = Trauma
    serializer_class = TraumaSerializer


class StaffMembershipViewSet(viewsets.ModelViewSet):
    model = StaffMembership

class ListTraumaMetadata(viewsets.ViewSet):
    def list(self, request):
        return Response({'trauma_types': get_model('mci','Trauma')._meta.get_field_by_name('trauma_type')[0].values,
                         'bodyparts' : get_model('mci','Trauma')._meta.get_field_by_name('bodypart')[0].values,
                         })