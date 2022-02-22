from django.db import models
from django.contrib.gis.db import models as gismodels


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields', None)
        if update_fields is not None:
            update_fields.append('modified_date')
        super(BaseModel, self).save(*args, **kwargs)


class Forecast(BaseModel):
    lat = models.DecimalField(max_digits=21, decimal_places=18)
    lon = models.DecimalField(max_digits=21, decimal_places=18)
    is_active = models.BooleanField(default=True)
    geom = gismodels.PointField(geography=True)
    fcat24 = models.DecimalField(max_digits=7, decimal_places=4)
    fcat48 = models.DecimalField(max_digits=7, decimal_places=4)
    gid = models.IntegerField(unique=True, db_index=True)
