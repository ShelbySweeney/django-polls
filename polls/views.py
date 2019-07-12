# -*- coding: utf-8 -*-
# from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.utils import timezone

from .models import Choice, Question


# Create your views here.

class IndexView(generic.ListView):
    # use the templates/polls/index.html template as a base
    template_name = 'polls/index.html'
    # The context is a dictionary mapping template variable names to Python objects
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future nor those that lack choices)
        """
        qlist = list()
        # gather a list of the published questions in chronological order,
        # not including those set to be published in the future
        qs = Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')

        # if there are no choices for a question, skip it; otherwise, add it
        # to the list of questions
        for q in qs:
            if len(q.choice_set.all()) == 0: continue
            else:
                qlist.append(q)

        # return the latest five
        return qlist[:5]




class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet and ones that don't
        have choices.
        """
        qlist = list()
        # gather a list of the published questions in chronological order,
        # not including those set to be published in the future
        qs = Question.objects.filter(pub_date__lte=timezone.now())

        # if there are no choices for a question, skip it; otherwise, add it
        # to the list of questions
        for q in qs:
            if len(q.choice_set.all()) == 0: continue
            else:
                qlist.append(q)

        return Question.objects.filter(question_text__in=qlist)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet and ones that don't
        have choices.
        """
        qlist = list()
        # gather a list of the published questions in chronological order,
        # not including those set to be published in the future
        qs = Question.objects.filter(pub_date__lte=timezone.now())

        # if there are no choices for a question, skip it; otherwise, add it
        # to the list of questions
        for q in qs:
            if len(q.choice_set.all()) == 0: continue
            else:
                qlist.append(q)

        return Question.objects.filter(question_text__in=qlist)


def vote(request, question_id):
    # Http404 if the object doesn’t exist
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form. The render() function takes the
        # request object as its first argument, a template name as its second
        # argument and a dictionary as its optional third argument. It returns
        # an HttpResponse object of the given template rendered with the given
        # context.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    else:
        # using this instead of selected_choice.votes+=1 prevents a race condition
        selected_choice.votes = F('votes') + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
