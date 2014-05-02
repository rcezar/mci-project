from django.db import models
from django.contrib.auth.models import User

# Defining class Enum
class EnumField(models.Field):
    """
    A field class that maps to MySQL's ENUM type.
    
    Usage:

    class Card(models.Model):
        suit = EnumField(values=('Clubs', 'Diamonds', 'Spades', 'Hearts'))

    c = Card()
    c.suit = 'Clubs'
    c.save()
    """

    def __init__(self, *args, **kwargs):
        self.values = kwargs.pop('values')
        kwargs['choices'] = [(v, v) for v in self.values]
        kwargs['default'] = self.values[0]
        super(EnumField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return "enum({0})".format(','.join("'%s'" % v for v in self.values))


# Create your models here.

class Person(models.Model):
    person_name = models.CharField(max_length=200)
    profession = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=200)
    cellphone_number = models.CharField(max_length=200)

    def __unicode__(self):
        return self.person_name


class Staff(models.Model):
    staff_name = models.CharField(max_length=200)
    members = models.ManyToManyField(Person, through='StaffMembership')

    def __unicode__(self):
        return self.staff_name


class StaffMembership(models.Model):
    person = models.ForeignKey(Person)
    staff = models.ForeignKey(Staff, related_name='memberships')
    role = EnumField(values=(
        'MEDICAL_COORDINATOR',
        'OPERATIONAL_COORDINATOR',
        'TRIAGE_COORDINATOR',
        'TREATMENT_COORDINATOR',
        'TRANSPORT_COORDINATOR',
        'MEMBER'))

    def __unicode__(self):
        return self.person.person_name + ' -  ' + self.role


class Incident(models.Model):
    incident_location = models.CharField(max_length=200, null=True)
    incident_name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True)
    staff = models.ForeignKey(Staff, null=True, blank=True)

    def __unicode__(self):
        return self.incident_name


class MCIUser(User):
    person = models.ForeignKey(Person, null=True, blank=True)
    #TODO change language to an ENUM type to system's available language
    language = models.CharField(max_length=10)


class PersonalData(models.Model):
    victim_name = models.CharField(max_length=200, null=True, blank=True)
    age = models.CharField(max_length=200, null=True, blank=True)
    gender = EnumField(values=(
        'MALE',
        'FEMALE'))
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    phone_number = models.CharField(max_length=200, null=True, blank=True)
    #TODO enum list with troubled-health-related religion 
    religion = models.CharField(max_length=200, null=True, blank=True)
    comments = models.CharField(max_length=400, null=True, blank=True)

    def __unicode__(self):
        s = 'n/a'
        n = 'n/a'
        if self.victim_name:
            n = self.victim_name
        if self.gender == 'MALE':
            s = 'M'
        elif self.gender == 'FEMALE':
            s = 'F'
        return n + ' -  ' + s + ' - ' + self.age


class Allergy(models.Model):
    personal_data = models.ForeignKey(PersonalData, related_name='allergies')
    allergy_name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.allergy_name


class Victim(models.Model):
    incident = models.ForeignKey(Incident, related_name='victims')
    tag_id = models.IntegerField(default=0)
    creation_time = models.DateTimeField('Creation Time')
    creation_agent = models.ForeignKey(User)
    personal_data = models.ForeignKey(PersonalData)

    def __unicode__(self):
        return 'tag ' + unicode(self.tag_id) + ' - ' + unicode(self.personal_data)


class StatusInfo(models.Model):
    victim = models.ForeignKey(Victim, related_name='status_info')
    status = EnumField(values=(
        'TRIAGE',
        'TREATMENT',
        'TRANSPORT'))
    agent = models.ForeignKey(User)
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return self.status


class Location(models.Model):
    victim = models.ForeignKey(Victim, related_name='locations')
    coordinates = models.CharField(max_length=200, null=True, blank=True)
    agent = models.ForeignKey(User)
    timestamp = models.DateTimeField()


class Trauma(models.Model):
    victim = models.ForeignKey(Victim, related_name='traumas')
    trauma_type = EnumField(values=(
        'BLUNT',
        'BURN',
        'C_SPINE',
        'CARDIAC',
        'CRUSHION',
        'FRACTURE',
        'LACERATION',
        'PENETRATING_INJURY',
        'OTHER'))
    ai_type = models.CharField(max_length=200, null=True, blank=True)
    bodypart = EnumField(values=(
        'HEAD',
        'FACE',
        'NECK',
        'SHOULDER',
        'CHEST',
        'ARM',
        'WRIST',
        'PALM',
        'ABDOMINAL',
        'GROIN',
        'LEG',
        'KNEE',
        'FOOT',
        'OTHER'))
    ai_bodypart = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    agent = models.ForeignKey(User)
    timestamp = models.DateTimeField()


class Photo(models.Model):
    victim = models.ForeignKey(Victim, related_name='photos')
    trauma = models.ForeignKey(Trauma, related_name='photos', null=True, blank=True)
    photo_address = models.CharField(max_length=200, null=True, blank=True)
    agent = models.ForeignKey(User)
    timestamp = models.DateTimeField()


class Drug(models.Model):
    drug_name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.drug_name


class UsedMedicine(models.Model):
    victim = models.ForeignKey(Victim, related_name='used_medicines')
    dose = models.CharField(max_length=200, null=True, blank=True)
    drug = models.ForeignKey(Drug)
    agent = models.ForeignKey(User)
    timestamp = models.DateTimeField()


class Procedure(models.Model):
    procedure_name = models.CharField(max_length=200)


class AppliedProcedure(models.Model):
    victim = models.ForeignKey(Victim, related_name='applied_procedures')
    procedure = models.ForeignKey(Procedure)
    ai_procedure = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    agent = models.ForeignKey(User)
    timestamp = models.DateTimeField()


class Start(models.Model):
    victim = models.ForeignKey(Victim)
    timestamp = models.DateTimeField()
    mental_state = models.BooleanField()
    respiration = EnumField(values=(
        'NONE',
        'UNDER30',
        'ABOVE30'))
    perfusion = EnumField(values=(
        'PULSE_OK',
        'CAP_UNDER_2SEC',
        'CAP_OVER_2SEC'))
    triage_status = EnumField(values=(
        'MORGUE',
        'IMMEDIATE',
        'DELAYED',
        'MINOR'))
    agent = models.ForeignKey(User)


class VitalSignsMeasure(models.Model):
    victim = models.ForeignKey(Victim, related_name='vital_signs_measures')
    timestamp = models.DateTimeField()
    blood_pressure = models.CharField(max_length=200, null=True, blank=True)
    pulse = models.CharField(max_length=200, null=True, blank=True)
    respiration = models.CharField(max_length=200, null=True, blank=True)
    agent = models.ForeignKey(User)


class Hospital(models.Model):
    hospital_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    coordinates = models.CharField(max_length=200, null=True, blank=True)
    beds = models.IntegerField(default=0)
    trauma_specialty = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    contact_name = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.hospital_name


class Vehicle(models.Model):
    vehicle_number = models.CharField(max_length=200, null=True, blank=True)
    driver = models.CharField(max_length=200, null=True, blank=True)
    coordinates = models.CharField(max_length=200, null=True, blank=True)


class Shipment(models.Model):
    hospital = models.ForeignKey(Hospital)
    vehicle = models.ForeignKey(Vehicle)
    route = models.CharField(max_length=200, null=True, blank=True)
    shipment_crew = models.ManyToManyField(Person, through='Crew')


class Crew(models.Model):
    shipment = models.ForeignKey(Shipment)
    person = models.ForeignKey(Person)
