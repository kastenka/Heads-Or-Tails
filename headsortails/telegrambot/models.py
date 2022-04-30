from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

GET_COINS_AFTER_REGISTRATION = 1000


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        unique=True,
        verbose_name='Telegram User ID'
    )
    username = models.CharField(
        max_length=32,
        verbose_name='Username'
    )

    def __str__(self):
        return f"{self.external_id} {self.username}"

    class Meta:
        verbose_name = 'Profile'


class Coins(models.Model):
    username = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name='Username'
    )
    coins = models.PositiveIntegerField(
        verbose_name='Number of coins'
    )

    def __str__(self):
        return f"{self.username} {self.coins}"

    class Meta:
        verbose_name = 'Coins'
        verbose_name_plural = 'Coins'


class GameHistory(models.Model):
    username = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name='Username'
    )
    bid = models.PositiveIntegerField(
        verbose_name='Size of bid'
    )
    result = models.BooleanField(
        verbose_name='Game result'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Game datetime'
    )

    def __str__(self):
        result = 'won' if self.result else 'lost'
        return f"Game {self.pk}: user {self.username} with rate={self.bid} {result} at {self.created_at}"

    class Meta:
        verbose_name = 'Game History'
        verbose_name_plural = 'Game History'


@receiver(post_save, sender=Profile)
def create_coins_account(sender, instance, created, **kwargs):
    Coins.objects.create(
        username=instance,
        coins=GET_COINS_AFTER_REGISTRATION
    )

