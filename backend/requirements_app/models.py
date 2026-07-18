from django.contrib.auth.models import AbstractUser
from django.db import models
from .utils import calculate_priority_score

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'Regular User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class RequirementRequest(models.Model):
    TYPE_CHOICES = [
        ('regulatory', 'Regulatory Compliance'),
        ('security', 'Security Vulnerability'),
        ('revenue', 'Revenue Growth'),
        ('cost', 'Cost Reduction'),
        ('bug', 'Bug'),
        ('optimization', 'Feature Optimization'),
    ]

    USERS_CHOICES = [
        ('<100', '<100'),
        ('100-500', '100-500'),
        ('500-1000', '500-1000'),
        ('>1000', '>1000'),
    ]

    REVENUE_CHOICES = [
        ('<50k', '<50k'),
        ('50k-300k', '50k-300k'),
        ('300k-1M', '300k-1M'),
        ('>1M', '>1M'),
    ]

    WORKLOAD_CHOICES = [
        ('pending', 'Pending'),
        ('large', 'Large'),
        ('medium', 'Medium'),
        ('small', 'Small'),
    ]

    URGENCY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('pending_review', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('confirmed', 'Confirmed'),
        ('in_development', 'In Development'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=255)
    summary = models.TextField()
    country = models.CharField(max_length=100)
    requirement_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    impacted_users = models.CharField(max_length=10, choices=USERS_CHOICES, null=True, blank=True)
    supplementary_materials = models.JSONField(default=list, blank=True)
    revenue_impact = models.CharField(max_length=10, choices=REVENUE_CHOICES, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    
    submission_date = models.DateTimeField(auto_now_add=True)
    workload = models.CharField(max_length=10, choices=WORKLOAD_CHOICES, default='pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_review')
    priority_score = models.IntegerField(null=True, blank=True)
    reject_reason = models.TextField(null=True, blank=True)
    estimated_completion_date = models.DateField(null=True, blank=True)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
    
    submitter = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='requirements')

    def save(self, *args, **kwargs):
        self.priority_score = calculate_priority_score(self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.submitter.username})"


class Attachment(models.Model):
    requirement = models.ForeignKey(RequirementRequest, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.requirement.name} - {self.file.name}"
