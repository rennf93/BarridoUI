from django.db import models
from django.contrib.auth import get_user_model


class DateTimeBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Score(DateTimeBase):
    STATUS = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("finished", "Finished"),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    data = models.FileField()
    policy = models.CharField(max_length=50)
    workflow = models.CharField(max_length=50)
    result = models.FileField(null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=20, default="pending")

    class Meta:
        verbose_name = "Score"
        verbose_name_plural = "Score"
        permissions = (
            ('score_access', 'Can access score'),
        )

    def __str__(self):
        return "Score - {}".format(self.created_at)
