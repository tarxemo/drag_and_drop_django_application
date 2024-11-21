from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from authApp.models import CustomUser
# Custom validators
def validate_template_name(value):
    if not value.isalnum():
        raise ValidationError("Template name should contain only alphanumeric characters.")

class BaseModel(models.Model):
    """
    Abstract base model to include created_at and updated_at timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Template(BaseModel):
    """
    Stores template information, including the name, slug, description, and user details.
    """
    name = models.CharField(max_length=255, unique=True, validators=[validate_template_name])
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="templates")
    version = models.IntegerField(default=1)
    parent_version = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        return self.name

class Tag(BaseModel):
    """
    Represents an HTML tag that can be added to templates.
    Supports nested tags via parent_tag and also drag-and-drop positioning.
    """
    tag_name = models.CharField(max_length=100, db_index=True)
    tag_type = models.CharField(max_length=50, choices=[('text', 'Text'), ('image', 'Image'), ('button', 'Button')])
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="tags", db_index=True)
    parent_tag = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    position = models.PositiveIntegerField()  # Position for ordering tags
    attributes = models.JSONField(default=dict)  # Stores dynamic attributes as JSON
    classes = models.JSONField(default=list)  # Stores CSS classes as JSON array
    content = models.TextField(blank=True, null=True)  # Inner content of the tag (e.g., text or HTML)
    is_container = models.BooleanField(default=False)  # Defines whether the tag can contain other tags

    class Meta:
        ordering = ['position']
        indexes = [
            models.Index(fields=['template']),
            models.Index(fields=['position']),
        ]

    def __str__(self):
        return f"<{self.tag_name}> in {self.template.name}"

class Image(BaseModel):
    """
    Stores images associated with templates or tags.
    """
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="images", db_index=True)
    image_file = models.ImageField(upload_to='tag_images/')
    alt_text = models.CharField(max_length=255, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)  # in bytes

    class Meta:
        indexes = [
            models.Index(fields=['tag']),
        ]

    def __str__(self):
        return f"Image for {self.tag.tag_name}"

class Attribute(BaseModel):
    """
    Represents custom attributes that can be assigned to tags.
    """
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="custom_attributes", db_index=True)
    attributes = models.JSONField(default=dict)  # Store dynamic attributes as a key-value JSON

    class Meta:
        indexes = [
            models.Index(fields=['tag']),
        ]

    def __str__(self):
        return f"Attributes for <{self.tag.tag_name}>"

class FieldSchema(BaseModel):
    """
    Defines dynamic field structures using JSON schema.
    """
    tag = models.OneToOneField(Tag, on_delete=models.CASCADE, related_name="field_schema")
    schema = models.JSONField(default=dict)

    def __str__(self):
        return f"Field schema for {self.tag.tag_name}"

class TemplateThumbnail(BaseModel):
    """
    Stores generated thumbnails for templates.
    """
    template = models.OneToOneField(Template, on_delete=models.CASCADE, related_name="thumbnail")
    image = models.ImageField(upload_to='template_thumbnails/')

    def __str__(self):
        return f"Thumbnail for {self.template.name}"

class TemplateVersion(BaseModel):
    """
    Represents historical versions of a template.
    """
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="versions", db_index=True)
    version_number = models.PositiveIntegerField()
    data_snapshot = models.JSONField()  # Store snapshot of template structure as JSON

    class Meta:
        unique_together = ('template', 'version_number')
        indexes = [
            models.Index(fields=['template']),
            models.Index(fields=['version_number']),
        ]

    def __str__(self):
        return f"Version {self.version_number} of {self.template.name}"

class CollaborationSession(BaseModel):
    """
    Tracks real-time collaboration sessions.
    """
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="collaboration_sessions", db_index=True)
    users = models.ManyToManyField(CustomUser, related_name='collaboration_sessions')
    session_token = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Collaboration session for {self.template.name}"

class TemplateUsageLog(BaseModel):
    """
    Logs usage of templates for analytics and tracks drag-and-drop actions.
    """
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="usage_logs", db_index=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # e.g., "created", "updated", "deleted", "dragged"
    user_agent = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['template']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Usage log for {self.template.name} by {self.user.username}"

class Role(models.Model):
    """
    Defines roles that can have a set of permissions associated with them.
    """
    name = models.CharField(max_length=50, unique=True, db_index=True)

    def __str__(self):
        return self.name

class TemplatePermission(models.Model):
    """
    Assigns permissions for templates to roles.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_index=True)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, db_index=True)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'template')
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['template']),
        ]

    def __str__(self):
        return f"Permissions for {self.role.name} on {self.template.name}"
