from django.contrib import admin
from .models import JournalEntry, Goal, Bookmark

admin.site.register(JournalEntry)
admin.site.register(Goal)
admin.site.register(Bookmark)
