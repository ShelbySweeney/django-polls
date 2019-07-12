# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Choice, Question

# put choices inside the question poll so choices can be entered from the
# question pages

# by default, provide enough fields for 3 choices. Use TabularInline instead of
# StackedInline so it displays it more compactly
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

# choice objects are edited on the Question admin page
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    # display multiple columns on the "change list" admin page
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    # allow filtering by publication date. Because pub_date is a DateTimeField,
    # Django knows to give appropriate filter options: “Any date”, “Today”,
    # “Past 7 days”, “This month”, “This year”.
    list_filter = ['pub_date']
    # allow searching by question text
    search_fields = ['question_text']

admin.site.register(Question, QuestionAdmin)
