from django.contrib import admin
from .models import Post, Comment, Profile, Like

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created', 'published')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created', 'active' )
    list_filter = ('active', 'created')
    actions = ['approve_comments']
    def approve_comments(self, request, queryset):
        queryset.update(active=True)
        # TODO: Вывод сообщений о успешной модерации нескольких комментариев одновременно
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(Like)
