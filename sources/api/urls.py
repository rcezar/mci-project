from django.conf.urls import patterns, include, url
from rest_framework_nested import routers
from api.views import *


##Routers
router_authentication = routers.SimpleRouter()
router_authentication.register(r'authenticate', AuthenticateViewSet, base_name=r'authenticate')

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

router_nested_victim = routers.NestedSimpleRouter(router_victim, r'victims')
router_nested_victim.register(r'traumas', TraumaNestedViewSet)

router_list_trauma_metadata = routers.SimpleRouter()
router_list_trauma_metadata.register(r'list_trauma_metadata', ListTraumaMetadata, base_name=r'list_trauma_metadata')

urlpatterns = patterns('',
                       url(r'^', include(router_authentication.urls)),
                       url(r'^', include(router_staffmember.urls)),
                       url(r'^', include(router_staff.urls)),
                       url(r'^', include(router_nested_staff.urls)),
                       url(r'^', include(router_victim.urls)),
                       url(r'^', include(router_person.urls)),
                       url(r'^', include(router_incident.urls)),
                       url(r'^', include(router_nested_incident.urls)),
                       url(r'^', include(router_list_trauma_metadata.urls)),
                       url(r'^', include(router_nested_victim.urls))
                       )
