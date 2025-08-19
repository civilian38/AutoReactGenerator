from django.db import models
from authentication.models import ARUser

class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(ARUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        owner_name = self.created_by.nickname if self.created_by.nickname else self.created_by.username
        return f'{owner_name} - {self.name}'