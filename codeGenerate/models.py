from django.db import models

from project.models import Project
from apidoc.models import APIDoc
from discussion.models import Discussion
from frontFile.models import Folder, ProjectFile
from frontPage.models import FrontPage

class GenerationSession(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', '진행 중'), 
        ('COMPLETED', '반영 완료'),
        ('DISCARDED', '폐기됨'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    # 필요 정보 취합
    related_apidocs = models.ManyToManyField(APIDoc, related_name='sessions')
    related_discussions = models.ManyToManyField(Discussion, related_name='sessions')
    related_folders = models.ManyToManyField(Folder, related_name='sessions')
    related_files = models.ManyToManyField(ProjectFile, related_name='sessions')
    related_pages = models.ManyToManyField(FrontPage, related_name='sessions')

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'({self.project}) {self.title}'

class SessionChat(models.Model):
    session_under = models.ForeignKey(GenerationSession, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_by_user = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.session_under} | {self.content[:30]}'