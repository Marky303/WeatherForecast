from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Entry(models.Model):
    time = models.DateField(null=True)
    temp = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    dwpt = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    rhum = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    prcp = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    wdir = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    wspd = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    pres = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    coco = models.IntegerField(
        validators=[
            MinValueValidator(0),  # Lower limit
            MaxValueValidator(27),  # Upper limit
        ],
        default = 0
    )

    # series' time value is "name"
    def add_entry(s):
        e = Entry(time=s.name,
                  temp=s.temp,
                  dwpt=s.dwpt,
                  rhum=s.rhum,
                  prcp=s.prcp,
                  wdir=s.wdir,
                  wspd=s.wspd,
                  pres=s.pres,
                  coco=s.coco)
        e.save()
        return 
    
    def __str__(self):
        return str(self.time) + " : " + str(self.temp) + " Cel"