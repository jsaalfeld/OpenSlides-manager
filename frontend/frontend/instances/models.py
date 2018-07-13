from django.db import models

# The Instance Itself
# This will be fed automatically, where the ID is the instance name.
# The instance name is equal to the folder name in the instances
#   folder on the hard drive
class Instance(models.Model):
    instance_name = models.CharField(max_length=255, primary_key=True)
    add_date = models.DateTimeField('date added')
    def __str__(self):
        return self.instance_name