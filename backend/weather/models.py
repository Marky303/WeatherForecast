from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Other libraries
import math
import pytz

# Global variables
dimensions = ['temp', 'dwpt', 'rhum', 'wdir', 'wspd', 'pres']

# Create your models here.
class Entry(models.Model):
    time = models.DateTimeField(null=True)
    temp = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    dwpt = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    rhum = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
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
        # Check if coco value is nan
        if (math.isnan(s.coco)):
            coco_check = 0
        else:
            coco_check = s.coco
            
        # Creating and saving a new entry
        e = Entry(time=s.name.replace(tzinfo=pytz.UTC),
                  temp=s.temp,
                  dwpt=s.dwpt,
                  rhum=s.rhum,
                  wdir=s.wdir,
                  wspd=s.wspd,
                  pres=s.pres,
                  coco=coco_check)
        e.save()
        return 
    
    def __str__(self):
        return str(self.time) + " : " + str(self.temp) + " Cel"
    
class Prediction(models.Model):
    # Time of prediction
    prediction_time = models.DateTimeField(null=True)
    
    # Number of predicted entries
    predicted_entry_count = models.IntegerField(default=0)
    
    # Accuracy of each prediction features
    accuracy_temp = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    accuracy_dwpt = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    accuracy_rhum = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    accuracy_wdir = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    accuracy_wspd = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    accuracy_pres = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    
    # Accuracy of the prediction generally
    accuracy = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    
    # ???
    def getPrediction(self):
        pass
    
    def __str__(self):
        return str(self.prediction_time) + " : " + str(self.accuracy)
    
class Predicted_Entry(models.Model):    
    # Foreign key to prediction
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    
    # predicted_Entry fields
    time = models.DateTimeField(null=True)
    temp = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    dwpt = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
    rhum = models.DecimalField(max_digits=6, decimal_places=1, default=-1)
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
    
    # Other predictions
    risk_of_rain = models.DecimalField(
        max_digits=6, 
        decimal_places=6,
        validators=[
            MinValueValidator(0),  # Lower limit
            MaxValueValidator(1),  # Upper limit
        ],
        default = 0
    )

    # series' time value is "name"
    def add_entry(s, prediction):   
        # TEST
        print(s)
        print(prediction)
             
        # Creating and saving a new entry
        e = Predicted_Entry(time=s.time.replace(tzinfo=pytz.UTC),
                  temp=round(s.temp,1),
                  dwpt=round(s.dwpt,1),
                  rhum=round(s.rhum,1),
                  wdir=round(s.wdir,1),
                  wspd=round(s.wspd,1),
                  pres=round(s.pres,1),
                  coco=round(s.coco,1),
                  prediction=prediction,
                  risk_of_rain=round(s.risk,4))
        e.save()
        return 
    
    def __str__(self):
        return str(self.time) + " : " + str(self.temp) + " Cel"