from django.contrib import admin
from mci.models import *

# Register your models here.

class VictimAdmin(admin.ModelAdmin):

    fieldsets = [
        (None,          {'fields': ['tag_id', 'creation_time']}),
        ('More info',   {'fields': ['incident', 'creation_agent', 'personal_data']}),
    ]
    list_display = ('tag_id', 'personal_data')

admin.site.register(Victim, VictimAdmin)


class UsedMedicineAdmin(admin.ModelAdmin):
     list_display = ('victim', 'drug', 'dose', 'agent', 'timestamp')
     
admin.site.register(UsedMedicine, UsedMedicineAdmin)

class HospitalAdmin(admin.ModelAdmin):
    list_display=('hospital_name', 'beds', 'trauma_specialty', 'address' )

admin.site.register(Hospital, HospitalAdmin)

admin.site.register(StatusInfo)

admin.site.register(Incident)
admin.site.register(Staff)
admin.site.register(StaffMembership)
admin.site.register(Person)
admin.site.register(MCIUser)
admin.site.register(Location)
admin.site.register(Photo)
admin.site.register(Trauma)
admin.site.register(PersonalData)
admin.site.register(Allergy)

admin.site.register(Drug)
admin.site.register(AppliedProcedure)
admin.site.register(Procedure)
admin.site.register(Shipment)
admin.site.register(Crew)
admin.site.register(Vehicle)

admin.site.register(VitalSignsMeasure)
admin.site.register(Start)