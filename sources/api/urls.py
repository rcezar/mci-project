from django.conf.urls import patterns, include, url
from rest_framework import viewsets, serializers, status
from rest_framework.response import Response
from mci.models import *
from rest_framework_nested import routers
from datetime import datetime
from django.contrib.auth.models import User
from django.core import serializers as core_serializers

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
        victim.tag_id = request.DATA['tag_id']
        victim.creation_time = datetime.now()
        victim.creation_agent = User.objects.get(pk=1) # FIXME: assign the proper creation agent
        pd = PersonalData()
        pd.gender = request.DATA['personal_data']['gender']
        pd.save()
        victim.personal_data = pd
        victim.save()
        return Response(data=VictimSerializer(victim).data, status=status.HTTP_201_CREATED)

    # TODO: find some way to remove GET from the options from url's like http://sitename/api/incidents/1/victims/2
    # TODO: this is better than returning a 403
    def retrieve(self, request, pk=None, nested_1_pk=None):
        return Response(status=status.HTTP_403_FORBIDDEN)


class PersonViewSet(viewsets.ModelViewSet):
    model = Person


class IncidentViewSet(viewsets.ModelViewSet):
    model = Incident


router_person = routers.SimpleRouter()
router_person.register(r'persons', PersonViewSet)

router_incident = routers.SimpleRouter()
router_incident.register(r'incidents', IncidentViewSet)

router_nested_incident = routers.NestedSimpleRouter(router_incident, r'incidents')
router_nested_incident.register(r'victims', VictimNestedViewSet)

urlpatterns = patterns('',
                       url(r'^', include(router_person.urls)),
                       url(r'^', include(router_incident.urls)),
                       url(r'^', include(router_nested_incident.urls)),
)

