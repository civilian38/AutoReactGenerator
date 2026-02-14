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

    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_occupied = models.BooleanField(default=False)

    # 필요 정보 취합
    related_apidocs = models.ManyToManyField(APIDoc, related_name='sessions', blank=True)
    related_discussions = models.ManyToManyField(Discussion, related_name='sessions', blank=True)
    related_folders = models.ManyToManyField(Folder, related_name='sessions', blank=True)
    related_files = models.ManyToManyField(ProjectFile, related_name='sessions', blank=True)
    related_pages = models.ManyToManyField(FrontPage, related_name='sessions', blank=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'({self.project_under}) {self.title}'

    def get_related_objects(self):
        return {
            'apidocs': self.related_apidocs.prefetch_related('request_bodies', 'response_bodies').all(),
            'discussions': self.related_discussions.all(),
            'folders': self.related_folders.all(),
            'files': self.related_files.all(),
            'pages': self.related_pages.all(),
        }

    def get_related_files(self):
        return {
            'files': self.related_files.all()
        }

class SessionChat(models.Model):
    session_under = models.ForeignKey(GenerationSession, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_by_user = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.session_under} | {self.content[:30]}'