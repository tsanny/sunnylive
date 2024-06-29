import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


def generate_stream_key():
    return str(uuid.uuid4()).replace("-", "")[:16]


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # balance to store the amount of donations received
    balance = models.DecimalField(default=0, max_digits=9, decimal_places=2)


class Stream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    is_live = models.BooleanField(default=False)
    stream_key = models.CharField(
        _("Stream key"),
        max_length=16,
        null=False,
        blank=False,
        unique=True,
        default=generate_stream_key,
    )

    def __str__(self):
        return f"{self.title} | {self.host}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    stream = models.ForeignKey(
        Stream,
        on_delete=models.CASCADE,
    )
    message = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}: "{self.message}" ({self.stream})'


class Donation(Comment):
    amount = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return f'{self.user} donated {self.amount}: "{self.message}" \
                ({self.stream})'

    def save(self, *args, **kwargs):
        user = CustomUser.objects.get(pk=self.stream.host.pk)
        user.balance += self.amount
        user.save()

        super(Donation, self).save(*args, **kwargs)
