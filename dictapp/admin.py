from django.contrib import admin


from .models import Word, WordUser


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'created_at')
    search_fields = ('word',)
    list_filter = ('created_at',)


@admin.register(WordUser)
class WordUserAdmin(admin.ModelAdmin):
    list_display = ('word', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('word__word', 'user__username')
