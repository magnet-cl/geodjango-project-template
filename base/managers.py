from django.contrib.auth.models import UserManager as DjangoUserManager
from django.contrib.gis.db import models

class UserManager(DjangoUserManager, models.GeoManager):
    pass
