from django.db import models
from project.models import Project
from authentication.models import ARUser

import json

HTTP_METHOD_CHOICES = [
    ('GET', 'GET'),
    ('POST', 'POST'),
    ('PUT', 'PUT'),
    ('DELETE', 'DELETE'),
    ('PATCH', 'PATCH'),
    ('HEAD', 'HEAD'),
    ('OPTIONS', 'OPTIONS'),
]

class HttpStatus(models.IntegerChoices):
    """
    HTTP 상태 코드 정의 (숫자형)
    """
    # 1xx: 정보
    HTTP_100_CONTINUE = 100, '100 Continue'
    HTTP_101_SWITCHING_PROTOCOLS = 101, '101 Switching Protocols'

    # 2xx: 성공
    HTTP_200_OK = 200, '200 OK'
    HTTP_201_CREATED = 201, '201 Created'
    HTTP_202_ACCEPTED = 202, '202 Accepted'
    HTTP_204_NO_CONTENT = 204, '204 No Content'
    HTTP_205_RESET_CONTENT = 205, '205 Reset Content'
    HTTP_206_PARTIAL_CONTENT = 206, '206 Partial Content'

    # 3xx: 리다이렉션
    HTTP_300_MULTIPLE_CHOICES = 300, '300 Multiple Choices'
    HTTP_301_MOVED_PERMANENTLY = 301, '301 Moved Permanently'
    HTTP_302_FOUND = 302, '302 Found'
    HTTP_304_NOT_MODIFIED = 304, '304 Not Modified'
    HTTP_307_TEMPORARY_REDIRECT = 307, '307 Temporary Redirect'
    HTTP_308_PERMANENT_REDIRECT = 308, '308 Permanent Redirect'

    # 4xx: 클라이언트 오류
    HTTP_400_BAD_REQUEST = 400, '400 Bad Request'
    HTTP_401_UNAUTHORIZED = 401, '401 Unauthorized'
    HTTP_403_FORBIDDEN = 403, '403 Forbidden'
    HTTP_404_NOT_FOUND = 404, '404 Not Found'
    HTTP_405_METHOD_NOT_ALLOWED = 405, '405 Method Not Allowed'
    HTTP_406_NOT_ACCEPTABLE = 406, '406 Not Acceptable'
    HTTP_408_REQUEST_TIMEOUT = 408, '408 Request Timeout'
    HTTP_409_CONFLICT = 409, '409 Conflict'
    HTTP_410_GONE = 410, '410 Gone'
    HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415, '415 Unsupported Media Type'
    HTTP_422_UNPROCESSABLE_ENTITY = 422, '422 Unprocessable Entity'
    HTTP_429_TOO_MANY_REQUESTS = 429, '429 Too Many Requests'

    # 5xx: 서버 오류
    HTTP_500_INTERNAL_SERVER_ERROR = 500, '500 Internal Server Error'
    HTTP_501_NOT_IMPLEMENTED = 501, '501 Not Implemented'
    HTTP_502_BAD_GATEWAY = 502, '502 Bad Gateway'
    HTTP_503_SERVICE_UNAVAILABLE = 503, '503 Service Unavailable'
    HTTP_504_GATEWAY_TIMEOUT = 504, '504 Gateway Timeout'

class URLParameter(models.Model):
    parameter = models.CharField(max_length=255)
    description = models.TextField()
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.parameter:
            self.parameter = "{" + self.parameter.strip("{}") + "}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_under} | {self.parameter}"

    def get_prompt_text(self):
        return f"{self.parameter} | {self.description}"
    
class APIDoc(models.Model):
    url = models.URLField(max_length=250)
    url_parameters = models.ManyToManyField(URLParameter, related_name="apidocs")
    http_method = models.CharField(max_length=20, choices=HTTP_METHOD_CHOICES, default='GET')
    method_order = models.IntegerField(default=0, db_index=True, editable=False)
    request_headers = models.JSONField(default=dict, blank=True)
    query_params = models.JSONField(default=dict, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(ARUser, on_delete=models.CASCADE)
    project_under = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.project_under} - ({self.http_method}){self.url}'
    
    class Meta:
        ordering = ['url', 'method_order']
    
    def save(self, *args, **kwargs):
        ordering_map = {
            'GET': 1,
            'POST': 2,
            'PUT': 3,
            'DELETE': 4,
            'PATCH': 5,
            'HEAD': 6,
            'OPTIONS': 7
        }
        self.method_order = ordering_map.get(self.http_method, 99)
        super().save(*args, **kwargs)
    
    def get_prompt_text(self):
        text = f"URL: {self.url}\n"
        if self.url_parameters.all():
            text += "URL parameter:\n"
            for parameter in self.url_parameters.all():
                text += parameter.get_prompt_text() + "\n"
        text += f"요청 종류: {self.http_method}\n"
        text += f"요청에 대한 설명: {self.description}\n"
        
        request_bodies = self.request_bodies.all()
        if request_bodies.exists():
            text += "\n[Request Bodies]\n"
            for req in request_bodies:
                text += f"- 설명: {req.description or '없음'}\n"
                text += f"  예시: {json.dumps(req.request_example, indent=2, ensure_ascii=False)}\n"
                text += "=" * 4 + "\n"

        response_bodies = self.response_bodies.all()
        if response_bodies.exists():
            text += "\n[Response Bodies]\n"
            for res in response_bodies:
                text += f"- 상태 코드: {res.http_status}\n"
                text += f"  설명: {res.description or '없음'}\n"
                text += f"  예시: {json.dumps(res.response_example, indent=2, ensure_ascii=False)}\n"
                text += "=" * 4 + "\n"
                
        text += "=" * 10
        
        return text

class APIRequestBody(models.Model):
    apidoc = models.ForeignKey(APIDoc, related_name='request_bodies', on_delete=models.CASCADE)
    request_example = models.JSONField(default=dict)
    description = models.TextField(default="", blank=True)
    
    def __str__(self):
        return f'{self.apidoc} | RequestBody({self.id})'

class APIResponseBody(models.Model):
    apidoc = models.ForeignKey(APIDoc, related_name='response_bodies', on_delete=models.CASCADE)

    http_status = models.PositiveSmallIntegerField(
        choices=HttpStatus.choices,
        default=HttpStatus.HTTP_200_OK,
    )

    description = models.TextField(default="", blank=True)

    response_example = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ['http_status']

    def __str__(self):
        return f"{self.apidoc} | [{self.http_status}] Response Sample"
