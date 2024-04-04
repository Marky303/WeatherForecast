from django.contrib import admin

# Import your models here
from .models import *

# Register your models here.
admin.site.register(Entry)
admin.site.register(Predicted_Entry)
admin.site.register(Prediction)
