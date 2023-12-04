from django.db import models

class Parcel(models.Model):
    id = models.IntegerField(primary_key=True)
    OBJECTID = models.CharField(max_length=100)
    FileNumber = models.CharField(max_length=100, null=True, blank=True)
    Name_of_Allottee = models.CharField(max_length=100, null=True, blank=True)
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
        return self.FileNumber + ' ' + self.Name_of_Allottee 



class Lines(models.Model):
    id = models.IntegerField(primary_key=True)
    OBJECTID = models.CharField(max_length=100, null=True, blank=True)
    ParcelID = models.ForeignKey(Parcel, on_delete=models.CASCADE)
    Length = models.CharField(max_length=100, null=True, blank=True)
    Sequence = models.CharField(max_length=50, null=True, blank=True)
    InternalAngle = models.CharField(max_length=30, null=True, blank=True)
    FromBeaconNo = models.CharField(max_length=100, null=True, blank=True)
    ToBeaconNo = models.CharField(max_length=100, null=True, blank=True)
    Direction = models.CharField(max_length=100, null=True, blank=True)
    Northings = models.CharField(max_length=100, null=True, blank=True)
    Eastings = models.CharField(max_length=100, null=True, blank=True)
    Dir1 = models.CharField(max_length=4, null=True, blank=True)
    Dir2 = models.CharField(max_length=4, null=True, blank=True)
    
    def __str__(self):
        return self.ParcelID


# class GeneratedBackCopy(models.Model):
#     FileNo = models.ForeignKey(Parcel, on_delete=models.CASCADE)
#     is_Generated = models.BooleanField(default=False)
#     Generated_by = models.CharField(max_length=100)
#     Generated_date = models.DateField(null=True, blank=True)


#     def __str__(self):
#         return self.FileNo