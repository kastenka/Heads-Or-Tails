from django.contrib import admin

from .models import Profile, Coins, GameHistory


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'username')


@admin.register(Coins)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'coins')


@admin.register(GameHistory)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'bid', 'result', 'created_at')



