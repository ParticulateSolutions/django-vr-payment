from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    last_modified = models.DateTimeField("Last modified", auto_now=True)

    class Meta:
        abstract = True
