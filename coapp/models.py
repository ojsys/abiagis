from django.db import models

class BackCopy(models.Model):
    abia_gis_fileno = models.CharField(max_length=100, null=True, blank=True)
    name_of_allotee = models.CharField(max_length=100)
    name_of_surveyor = models.CharField(max_length=100, null=True, blank=True)
    landuse = models.CharField(max_length=100, null=True, blank=True)
    spacial_lga = models.CharField(max_length=100, null=True, blank=True)
    lga = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    plan_no = models.CharField(max_length=100, null=True, blank=True)
    plot_no = models.CharField(max_length=100, null=True, blank=True)
    prepared_by = models.CharField(max_length=100, null=True, blank=True)
    prepared_date = models.DateField(null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return self.abia_gis_fileno + ' ' + self.name_of_allotee 

