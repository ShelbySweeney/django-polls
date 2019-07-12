# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.

@python_2_unicode_compatible    # only if you need to support Python 2
class Question(models.Model):
    # the name of each Field instance (e.g., question_text) is the machine-readable name
    # it's used in Python code and the database column name
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')    # this defines a human-readable name for Question.pub_date

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    # for the admin page, order by published date, show a checkmark if
    # published recently, and an x if not. Make the column header "Published
    # recently?" instead of the default "Was Published Recently"
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


@python_2_unicode_compatible    # only if you need to support Python 2
class Choice(models.Model):
    # the ForeignKey defines a relationship that tells Django each Choice is related to a single Question
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text
