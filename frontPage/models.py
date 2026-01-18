from django.db import models
from project.models import Project

class FrontPage(models.Model):
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)
    url = models.URLField()
    page_description = models.TextField()
    is_implemented = models.BooleanField(default=False)

    def __str__(self):
        return f'[{self.id}] {self.project_under.name} - {self.url}'
    
    def get_prompt_text(self):
        text = "URL - 다음 URL로 요청이 들어왔을 때의 페이지를 만드시오: " + self.url + "\n"
        text += "페이지는 다음과 같은 기능을 해야 합니다:\n" + self.page_description + "\n" 

        return text