from django.db import models

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=64)
    alternative_name = models.CharField(max_length=64, null=True, blank=True)
    bangle_name = models.CharField(max_length=64, null=True, blank=True)
    retail_unit = models.CharField(max_length=64)
    bulk_wholesale_unit = models.CharField(max_length=64, null=True, blank=True)
    price_per_retail_unit = models.FloatField(default=0, null=True, blank=True)
    price_per_bulk_wholesale_unit = models.FloatField(default=0, null=True, blank=True)
    bulk_to_retail_unit = models.FloatField(default=1, null=True, blank=True)
    DateAdded = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.name