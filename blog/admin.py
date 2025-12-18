from django.contrib import admin
from .models import Post, Comment, Profile, Like

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created', 'published')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created', 'active')
    list_filter = ('active', 'created')

admin.site.register(Profile)
admin.site.register(Like)
