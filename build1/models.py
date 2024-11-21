from django.db import models
from authApp.models import CustomUser


class BaseModel(models.Model):
    """
    Abstract base model to include created_at and updated_at timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
         
class Application(BaseModel):
    application_name = models.CharField(max_length=50)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class ApplicationUrls(BaseModel):
    Application = models.ForeignKey(Application, on_delete=models.CASCADE)
    relative_url_name = models.CharField(max_length=50)

class Template(BaseModel):
    template_name = models.CharField(max_length=50)
    
class Functionality(BaseModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    functionality_name = models.CharField(max_length=50)
