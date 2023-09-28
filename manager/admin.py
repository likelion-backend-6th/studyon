from django.contrib import admin

from markdownx.admin import MarkdownxModelAdmin

from .models import Study, Task, Post, File


admin.site.register(Study)
admin.site.register(Task)
admin.site.register(Post, MarkdownxModelAdmin)
admin.site.register(File)
