from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from authApp.models import CustomUser  
from django.db import transaction
from django.conf import settings


class Project(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=100, blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="projects")
    applications = models.ManyToManyField('Application', related_name='projects')  # Many-to-many relationship
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
class Application(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="applications")
    

class Template(models.Model):
    CATEGORY_CHOICES = [
        ('CATEGORY_1', 'Category 1'),
        ('CATEGORY_2', 'Category 2'),
        ('CATEGORY_3', 'Category 3'),
    ]
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user", null=True)

    def __str__(self):
        return self.name
    
class Like(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use the correct user model
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('template', 'user')  # Ensures one like per user per template

    def __str__(self):
        return f'{self.user.username} likes {self.template.name}'
    
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

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                existing_tag = Tag.objects.get(pk=self.pk)
                if existing_tag.parent_tag != self.parent_tag:
                    max_position = (
                        Tag.objects.filter(parent_tag=self.parent_tag)
                        .aggregate(max_position=models.Max('position'))
                        .get('max_position')
                    )
                    self.position = (max_position or 0) + 1
            else:
                max_position = (
                    Tag.objects.filter(parent_tag=self.parent_tag)
                    .aggregate(max_position=models.Max('position'))
                    .get('max_position')
                )
                self.position = (max_position or 0) + 1

            super().save(*args, **kwargs)

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
    class_name = models.CharField(max_length=50, unique=True)

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
    
    

# class TemplatesOwnership(models.Model):
#     application = models.ForeignKey(Application, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)  # Remove unique=True
#     category = models.ForeignKey(TemplateCategory, on_delete=models.SET_NULL, null=True, related_name="templates")

#     def __str__(self):
#         return f"{self.name} ({self.category.name if self.category else 'Uncategorized'})"


