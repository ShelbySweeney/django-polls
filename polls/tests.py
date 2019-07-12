# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Question
from .models import Choice

# Create your tests here.

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)



def create_question(question_text, days):
    """
    Create a question with the given 'question_text' and published the
    given number of 'days' offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        # since no questions have been created in this test.py script so far, it
        # shouldn't find any
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        pquest = create_question(question_text="Past question.", days=-30)
        pquest.choice_set.create(choice_text='pchoice', votes=0)
        response = self.client.get(reverse('polls:index'))
        # since only one question has been created in this script so far, it
        # is the only one that will be displayed
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        fquest = create_question(question_text="Future question.", days=30)
        fquest.choice_set.create(choice_text='fchoice', votes=0)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_current_question(self):
        """
        Questions with a pub_date of today are displayed on the
        index page.
        """
        cquest = create_question(question_text="Current question.", days=0)
        cquest.choice_set.create(choice_text='cchoice', votes=0)
        response = self.client.get(reverse('polls:index'))
        # verify the current question is displayed
        self.assertContains(response, cquest)


    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        pquest = create_question(question_text="Past question.", days=-30)
        pquest.choice_set.create(choice_text='pchoice', votes=0)
        fquest = create_question(question_text="Future question.", days=30)
        fquest.choice_set.create(choice_text='fchoice', votes=0)
        response = self.client.get(reverse('polls:index'))
        # verify the past question is displayed
        self.assertContains(response, pquest)
        # verify the future question is not displayed
        self.assertNotContains(response, fquest)


    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        pquest1 = create_question(question_text="Past question 1.", days=-30)
        pquest1.choice_set.create(choice_text='pchoice1', votes=0)
        pquest2 = create_question(question_text="Past question 2.", days=-5)
        pquest2.choice_set.create(choice_text='pchoice2', votes=0)
        response = self.client.get(reverse('polls:index'))
        # verify the response contains both past questions
        self.assertContains(response, pquest1)
        self.assertContains(response, pquest2)


    def test_future_question_and_past_question_and_current_question(self):
        """
        Even if past, current and future questions exist, only past and current
        questions are displayed.
        """
        # create past, future and current questions with choices
        pquest = create_question(question_text="Past question.", days=-30)
        pquest.choice_set.create(choice_text='pchoice1', votes=0)
        pquest.choice_set.create(choice_text='pchoice2', votes=0)
        fquest = create_question(question_text="Future question.", days=30)
        fquest.choice_set.create(choice_text='fchoice', votes=0)
        cquest = create_question(question_text="Current question.", days=0)
        cquest.choice_set.create(choice_text='cchoice', votes=0)

        response = self.client.get(reverse('polls:index'))

        # verify the response contains the current and past questions
        self.assertContains(response, cquest)
        self.assertContains(response, pquest)
        # verify the response does not contain future question
        self.assertNotContains(response, fquest)

    def test_question_without_choices(self):
        """
        Only questions that have choices are displayed.
        """
        # create a question with choices
        choiceq = create_question(question_text="Choices", days=-1)
        choiceq.choice_set.create(choice_text='choice1', votes=0)
        # create a question without choices
        no_choiceq = create_question(question_text="No choices", days=-1)
        response = self.client.get(reverse('polls:index'))
        # verify response doesn't contain the question without choices
        self.assertNotContains(response, no_choiceq)



class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        future_question.choice_set.create(choice_text='future choice', votes=0)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        past_question.choice_set.create(choice_text='past choice', votes=0)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_current_question(self):
        """
        The detail view of a question with pub_date of today
        displays the question's text.
        """
        # create a current question with two choices, one of which has 1 vote
        current_question = create_question(question_text='Current Question.', days=0)
        current_question.choice_set.create(choice_text='current choice', votes=0)
        current_question.choice_set.create(choice_text='current choice 2', votes=1)
        url = reverse('polls:detail', args=(current_question.id,))
        response = self.client.get(url)
        self.assertContains(response, current_question.question_text)

    def test_question_without_choices(self):
        """
        There are only detail views for questions with choices. Detail view for
        question without a choice returns 404 not found.
        """
        # create a question with a choice
        choiceq = create_question(question_text="Choices", days=-1)
        choiceq.choice_set.create(choice_text='choice1', votes=0)
        # create a question with no choices
        nochoiceq = create_question(question_text="No choices", days=-1)
        # define urls and responses for the questions
        url_choice = reverse('polls:detail', args=(choiceq.id,))
        url_nochoice = reverse('polls:detail', args=(nochoiceq.id,))
        response_choice = self.client.get(url_choice)
        response_nochoice = self.client.get(url_nochoice)
        # check if the question with choices returns the choices and question text
        self.assertContains(response_choice, choiceq.question_text)
        # check if the question without choices returns 404 not found
        self.assertEqual(response_nochoice.status_code, 404)




class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        future_question.choice_set.create(choice_text='future choice', votes=0)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results view of a question with pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        past_question.choice_set.create(choice_text='past choice', votes=0)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_current_question(self):
        """
        The results view of a question with pub_date of today
        displays the question's text.
        """
        current_question = create_question(question_text='Current Question.', days=0)
        current_question.choice_set.create(choice_text='current choice', votes=0)
        url = reverse('polls:results', args=(current_question.id,))
        response = self.client.get(url)
        self.assertContains(response, current_question.question_text)

    def test_question_without_choices(self):
        """
        Results view for a question without choices returns 404 not found.
        """
        nochoiceq = create_question(question_text="No choices", days=-1)
        url_nochoice = reverse('polls:detail', args=(nochoiceq.id,))
        response_nochoice = self.client.get(url_nochoice)
        self.assertEqual(response_nochoice.status_code, 404)
