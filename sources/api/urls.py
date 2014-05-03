from django.conf.urls import patterns, include, url
from rest_framework import viewsets, serializers, status
from rest_framework.response import Response
from mci.models import *
from rest_framework_nested import routers
from datetime import datetime
from django.contrib.auth.models import User
from django.core import serializers as core_serializers


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


class VictimSerializer(serializers.ModelSerializer):
    personal_data = PersonalDataSerializer(source='personal_data')
    class Meta:
        model = Victim
        #fields = ('id', 'incident', 'tag_id', 'creation_time', 'creation_agent', 'personal_data')


# Victims related to Incidents with url such as http://sitename/api/incidents/1/victims/2
class VictimNestedViewSet(viewsets.ViewSet):
    model = Victim
    def list(self, request, nested_1_pk=None):
        incident = Incident.objects.get(pk=nested_1_pk)
        victims = incident.victims.all()
        serializer = VictimSerializer(victims, many=True)
        return Response(serializer.data)

    def create(self, request, nested_1_pk):
        victim = Victim()
        incident = Incident.objects.get(pk=nested_1_pk)
        l = dir(request)
        p = request.DATA
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
    def retrieve(self, request, pk=None, nested_1_pk=None):
        return Response(status=status.HTTP_403_FORBIDDEN)


class StaffMembershipNestedViewSet(viewsets.ViewSet):
    model = StaffMembership
    def list(self, request, nested_1_pk=None):
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

class StaffMembershipViewSet(viewsets.ModelViewSet):
    model = StaffMembership
    #serializer_class = StaffMembershipSerializer

##Routers
router_staffmember = routers.SimpleRouter()
router_staffmember.register(r'staffmembers', StaffMembershipViewSet)

router_staff = routers.SimpleRouter()
router_staff.register(r'staffs', StaffViewSet)

router_victim = routers.SimpleRouter()
router_victim.register(r'victims', VictimViewSet)

router_person = routers.SimpleRouter()
router_person.register(r'persons', PersonViewSet)

router_incident = routers.SimpleRouter()
router_incident.register(r'incidents', IncidentViewSet)

router_nested_incident = routers.NestedSimpleRouter(router_incident, r'incidents')
router_nested_incident.register(r'victims', VictimNestedViewSet)

router_nested_staff = routers.NestedSimpleRouter(router_staff, r'staffs')
router_nested_staff.register(r'members', StaffMembershipNestedViewSet)

urlpatterns = patterns('',
                       url(r'^', include(router_staffmember.urls)),
                       url(r'^', include(router_staff.urls)),
                       url(r'^', include(router_nested_staff.urls)),
                       url(r'^', include(router_victim.urls)),
                       url(r'^', include(router_person.urls)),
                       url(r'^', include(router_incident.urls)),
                       url(r'^', include(router_nested_incident.urls)),
)

