from django.db import models

# Create your models here.



class Chripsounder(models.Model):
    name_of_transmitter = models.CharField('Name of transmitter',max_length=30)
    tx_code = models.CharField(max_length=30, default=None)
    lat = models.CharField(max_length=30)
    longitude = models.CharField(max_length=30)
    range_zero = models.CharField('Range ground',max_length=30)
    chriprate = models.CharField(max_length=30)
    first_hop_range_one = models.IntegerField(default=0)
    first_hop_range_two = models.IntegerField(default=0)
    second_hop_range_one = models.IntegerField(default=0)
    second_hop_range_two = models.IntegerField(default=0)
    # this is receiver
    receiver_code = models.CharField('Receiver Code', max_length=100)
    deleted = models.BooleanField(default=False)


    class Meta:
        verbose_name = "Chirpsounder"


    def __str__(self):
        return self.name_of_transmitter


    


class ReceiverInfos(models.Model):
    receiver_name = models.CharField('Receiver Name:-', max_length=100)
    receiver_code = models.CharField('Receiver Code:-', max_length=100)
    receiver_location = models.CharField('Receiver Location:-', max_length=100)
    receiver_lat = models.CharField('Receiver Lat:-', max_length=100)
    receiver_long = models.CharField('Receiver Long:-', max_length=100)
    deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "ReceiverInfo"

    def __str__(self) -> str:
        return self.receiver_name


    



class DirectoryInfos(models.Model):
    root_dir = models.CharField('Root Directory Path:-', max_length=100)
    output_dir = models.CharField('Output Directory Path:-', max_length=100)
    input_dir = models.CharField('Input Directory Path:-', max_length=100)


    class Meta:
        verbose_name = "DirectoryInfo"

    def __str__(self) -> str:
        return self.root_dir



    

