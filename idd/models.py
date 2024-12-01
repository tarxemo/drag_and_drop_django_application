from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from authApp.models import CustomUser  

class Application(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="applications")
    
class Template(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    template = models.ForeignKey(Template, related_name='tags', on_delete=models.CASCADE)
    parent_tag = models.ForeignKey('self', related_name='children', null=True, blank=True, on_delete=models.CASCADE)
    tag_name = models.CharField(max_length=50)
    text_content = models.TextField(blank=True)
    classes = models.ManyToManyField('Class', related_name='tags', through='TagClass')
    django_tag_type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        choices=[
            ('csrf_token', 'CSRF Token'),
            ('for', 'For Loop'),
            ('endfor', 'End For Loop'),
            ('if', 'If Condition'),
            ('endif', 'End If Condition'),
            ('block', 'Block Tag'),
            ('endblock', 'End Block Tag'),
            ('extends', 'Extends Tag'),
            # Add more tags as needed
        ]
    )
    position = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('position', 'parent_tag')

    def __str__(self):
        return f"{self.tag_name} - {self.django_tag_type} at position {self.position}"

    
class Image(models.Model):
    image = models.ImageField(upload_to="images/")
    tag = models.OneToOneField(Tag,related_name='image', on_delete=models.CASCADE)
    
class Attribute(models.Model):
    tag = models.ForeignKey(Tag, related_name='attributes', on_delete=models.CASCADE)
    attribute_name = models.CharField(max_length=50)
    attribute_value = models.CharField(max_length=255)

    class Meta:
        unique_together = ('tag', 'attribute_name')

    def __str__(self):
        return f"{self.attribute_name}={self.attribute_value}"

class Class(models.Model):
    class_name = models.CharField(max_length=50)

    def __str__(self):
        return self.class_name

class TagClass(models.Model):
    tag = models.ForeignKey(Tag, related_name="tagclasses", on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tag', 'class_name')

class Table(models.Model):
    table_name = models.CharField(max_length=50)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class Book(models.Model):
    name = models.CharField(max_length=50)
    
    
class TemplateCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class TemplatesOwnership(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Remove unique=True
    category = models.ForeignKey(TemplateCategory, on_delete=models.SET_NULL, null=True, related_name="templates")

    def __str__(self):
        return f"{self.name} ({self.category.name if self.category else 'Uncategorized'})"

    
