from django.db import models

class Parcel(models.Model):
    OBJECTID = models.CharField(max_length=100)
    FileNumber = models.CharField(max_length=100, null=True, blank=True)
    Name_of_Allotee = models.CharField(max_length=100)
    Name_of_Surveyor = models.CharField(max_length=100, null=True, blank=True)
    Landuse = models.CharField(max_length=100, null=True, blank=True)
    LGA = models.CharField(max_length=100, null=True, blank=True)
    District = models.CharField(max_length=100, null=True, blank=True)
    Address = models.CharField(max_length=100, null=True, blank=True)
    Plan_No = models.CharField(max_length=100, null=True, blank=True)
    Location = models.CharField(max_length=100, null=True, blank=True)
    Plot_No = models.CharField(max_length=100, null=True, blank=True)
    State = models.CharField(max_length=100, null=True, blank=True)
    R_Particulars = models.CharField(max_length=100, null=True, blank=True)
    Starting_Pillar_No = models.CharField(max_length=100, null=True, blank=True)
    StatedArea = models.CharField(max_length=100, null=True, blank=True)
    Picture = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.abia_gis_fileno + ' ' + self.name_of_allotee 



class Lines(models.Model):
    OBJECTID = models.CharField(max_length=100)
    ParcelID = models.ForeignKey(Parcel, on_delete=models.CASCADE)
    Length = models.CharField(max_length=100)
    Sequence = models.CharField(max_length=50)
    InternalAngle = models.CharField(max_length=30)
    FromBeaconNo = models.CharField(max_length=100)
    ToBeaconNo = models.CharField(max_length=100)
    Direction = models.CharField(max_length=100)
    Northings = models.CharField(max_length=100)
    Eastings = models.CharField(max_length=100)
    
    def __str__(self):
        return self.parcelid


class GeneratedBackCopy(models.Model):
    FileNo = models.ForeignKey(Parcel, on_delete=models.CASCADE)
    is_Generated = models.BooleanField(default=False)
    Generated_by = models.CharField(max_length=100)
    Generated_date = models.DateField(null=True, blank=True)


    def __str__(self):
        return self.FileNo