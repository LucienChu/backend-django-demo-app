import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Question
from django.urls import reverse

# subclass for TestCase
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
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        # go to index page "/polls/"
        response = self.client.get(reverse('polls:index'))
        # check status
        self.assertEqual(response.status_code, 200)

        # check against the message for no polls within index.html
        self.assertContains(response, "No polls are available.")

        # check against values in 'latest-question-list' is empty
        # key name 'latest_question_list' is defined in class IndexView in polls/views.py file 
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """

        # create a pass question
        question = create_question(question_text="Past question.", days=-30)

        # go to index page "/polls/"
        response = self.client.get(reverse('polls:index'))

        # assert the question is displayed on the index page
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """

        # create question should be publish in 30 days
        create_question(question_text="Future question.", days=30)

        # go to index page "/polls/"
        response = self.client.get(reverse('polls:index'))

        # assert the question is not displayed on the index page
        self.assertContains(response, "No polls are available.")

        # NOTE: due to database would be reset for each test, so it should be 
        # response.context['latest_question_list'] is an empty list, rather than
        # have a past question created from previous test
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """

        # create a question which should not be displayed
        future_question = create_question(question_text='Future question.', days=5)

        # go to "/polls/future_question_id/"
        url = reverse('polls:detail', args=(future_question.id,))
        print("url", url)
        response = self.client.get(url)
        
        # have no idea why it raise 404 error over here
        # assume that this is the default behavior of the
        # generic.DetailView
        # when nothing, in current setup - [], is passed in, it MIGHT setup to
        # raise 404 error
        # see class DetailView in "polls/views.py"
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """

        # create a question which should be displayed
        past_question = create_question(question_text='Past Question.', days=-5)

        # go to "/polls/past_question_id/"
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)

        # assert past_question's text is display on the UI
        self.assertContains(response, past_question.question_text)