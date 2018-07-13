from django.db import models

class BackendConfig(models.Model):
    backend_url = models.CharField(max_length=2048)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.backend_url
