from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import QuizUserScore, Otp, Video, \
    Category, CourseSuggession, PlayerActivity, Feedback, Question
import json
from datetime import timedelta
from django.utils import timezone
import pytz


# Employee quiz score
class QuizUserScoreModelTestCase(TestCase):
    def setUp(self):
        # Create a test user for the foreign key relation
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@ratnaglobaltech.com'
        )

    def test_score_creation(self):
        # Create a QuizUserScore instance
        score = QuizUserScore.objects.create(
            user=self.user,
            quiz_domain='Python',
            score=80,
        )

        # Check if the QuizUserScore instance was created successfully
        self.assertEqual(QuizUserScore.objects.count(), 1)
        saved_score = QuizUserScore.objects.get(pk=score.pk)
        self.assertEqual(saved_score.quiz_domain, 'Python')
        self.assertEqual(saved_score.score, 80)

    def test_created_at_auto_generation(self):
        # Create a QuizUserScore instance without providing a created_at value
        score = QuizUserScore.objects.create(
            user=self.user,
            quiz_domain='Hadoop',
            score=30,
        )

        # Ensure that the created_at field is automatically generated
        self.assertIsNotNone(score.created_at)

        current_time = timezone.localtime(
            timezone.now(),
            pytz.timezone('Asia/Kolkata')
        )
        # Convert both datetimes to timezone-aware and compare
        score_time_aware = score.created_at.astimezone(
            pytz.timezone('Asia/Kolkata')
        )
        self.assertAlmostEqual(
            score_time_aware,
            current_time,
            delta=timezone.timedelta(seconds=1)
        )


class OtpModelTestCase(TestCase):
    def setUp(self):
        # Create a test user for the foreign key relation
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@ratnaglobaltech.com'
        )

    def test_otp_creation(self):
        otp = Otp.objects.create(
            user=self.user,
            mail='testuser@ratnaglobaltech.com',
            otp='1245',
            count='0',
            assigned_to='test@ratnaglobaltech.com'
        )
        # Check if the Otp instance was created successfully
        self.assertEqual(Otp.objects.count(), 1)
        saved_otp = Otp.objects.get(pk=otp.pk)
        self.assertEqual(saved_otp.user, self.user)
        self.assertEqual(saved_otp.mail, 'testuser@ratnaglobaltech.com')
        self.assertEqual(saved_otp.otp, '1245')
        self.assertEqual(saved_otp.count, 0)
        self.assertEqual(saved_otp.assigned_to, 'test@ratnaglobaltech.com')

    def test_default_values(self):
        # Create an Otp instance without specifying default values
        otp = Otp.objects.create(
            user=self.user,
            mail='testuser@ratnaglobaltech.com',
            otp='1245',
        )

        # Check if the default values were applied
        saved_otp = Otp.objects.get(pk=otp.pk)
        self.assertIsNone(saved_otp.assigned_to)
        self.assertEqual(saved_otp.count, 0)


# Employee Feedback
class FeedbackModelTestCase(TestCase):
    def setUp(self):
        # Create a test user for the foreign key relation
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@ratnaglobaltech.com'
        )

    def test_feedback_creation(self):
        # Create a Feedback instance
        feedback = Feedback.objects.create(
            user=self.user,
            overall_exp_with_STS='1',
            expectation_in_assisting_tech_transition='2',
            udm_yt_recom_helpful='5',
            cs_align_withur_curt_knowledge_levl='4',
            conveniency_accessing_recom_yt_cs='5',
            valueof_progs_tracking_feature_on_dashboard='5',
            motivate_to_complete_course='yes',
            specific_feature_you_feel_missing='Advanced search functionality',
            how_app_enhanced='Improved content recommendations',
            technical_prob_performance_issue='Slow video loading',
        )

        # Check if the Feedback instance was created successfully
        self.assertEqual(Feedback.objects.count(), 1)
        saved_feedback = Feedback.objects.get(pk=feedback.pk)
        self.assertEqual(saved_feedback.overall_exp_with_STS, '1')
        self.assertEqual(
            saved_feedback.expectation_in_assisting_tech_transition,
            '2'
        )


class VideoModelTestCase(TestCase):
    def setUp(self):
        # Create a Category instance for the foreign key relation
        self.category = Category.objects.create(category_name='Python')

    def test_video_creation(self):
        # Create a Video instance
        video = Video.objects.create(
            title='Introduction to Python',
            difficulty='BG',
            video_id='abc123',
            duration=timedelta(minutes=15),
            technology_v=self.category,
        )

        # Check if the Video instance was created successfully
        self.assertEqual(Video.objects.count(), 1)
        saved_video = Video.objects.get(pk=video.pk)
        self.assertEqual(saved_video.title, 'Introduction to Python')
        self.assertEqual(saved_video.difficulty, 'BG')
        self.assertEqual(saved_video.video_id, 'abc123')
        self.assertEqual(saved_video.duration, timedelta(minutes=15))
        self.assertEqual(saved_video.technology_v, self.category)


class CategoryModelTestCase(TestCase):

    def test_category_creation(self):
        category = Category.objects.create(category_name='Python')

        self.assertEqual(Category.objects.count(), 1)
        saved_category = Category.objects.get(pk=category.pk)
        self.assertEqual(saved_category.category_name, 'Python')


class CourseSuggestionModelTestCase(TestCase):
    def setUp(self):
        # Create a Category instance for the foreign key relation
        self.category = Category.objects.create(category_name='Python')

    def test_course_suggestion_creation(self):
        # Create a CourseSuggestion instance
        suggestion = CourseSuggession.objects.create(
            technology=self.category,
            course_url='https://example.com/python-course',
            difficulty='BG',
            course_name='Python Basics',
            course_instructor='John Doe',
            ratings=4.5,
            course_duration=10.5,
        )

        # Check if the CourseSuggestion instance was created successfully
        self.assertEqual(CourseSuggession.objects.count(), 1)
        saved_suggestion = CourseSuggession.objects.get(pk=suggestion.pk)
        self.assertEqual(saved_suggestion.technology, self.category)
        self.assertEqual(
            saved_suggestion.course_url,
            'https://example.com/python-course'
        )
        self.assertEqual(saved_suggestion.difficulty, 'BG')
        self.assertEqual(saved_suggestion.course_name, 'Python Basics')
        self.assertEqual(saved_suggestion.course_instructor, 'John Doe')
        self.assertEqual(saved_suggestion.ratings, 4.5)
        self.assertEqual(saved_suggestion.course_duration, 10.5)


class PlayerActivityModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@ratnaglobaltech.com'
        )

    def test_playeractivity_creation(self):
        playeractivity = PlayerActivity.objects.create(
            user=self.user,
            current_time=36789.0,
            youtube_id="dQw4w9WgXcQ",
            percentage=25.6,
            category='Python'
        )

        self.assertEqual(PlayerActivity.objects.count(), 1)
        saved_playeractivity = PlayerActivity.objects.get(pk=playeractivity.pk)
        self.assertEqual(saved_playeractivity.current_time, 36789)
        self.assertEqual(saved_playeractivity.youtube_id, "dQw4w9WgXcQ")
        self.assertEqual(saved_playeractivity.percentage, 25.6)
        self.assertEqual(saved_playeractivity.category, 'Python')


class IndexViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()  # Initialize the client
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@ratnaglobaltech.com'
        )
        self.session = self.client.session
        self.session['mail'] = 'testuser@ratnaglobaltech.com'
        self.session.save()

    def test_index_view_with_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home:index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_index_view_with_user_quiz_attempt(self):
        quiz_score = QuizUserScore.objects.create(user=self.user, score=10)
        # Re-fetch the user to ensure accuracy
        self.user = User.objects.get(email='testuser@ratnaglobaltech.com')

        self.client.force_login(self.user)
        response = self.client.get(reverse('home:index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        quiz_score.delete()


# Test Case
class QuizViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@ratnaglobaltech.com'
        )
        self.client = Client()
        self.client.login(
            username='testuser',
            email='testuser@ratnaglobaltech.com'
        )
        self.session = self.client.session
        self.session['mail'] = 'testuser@ratnaglobaltech.com'
        self.session.save()

    def test_quiz_view(self):
        # Ensure the client is logged in before making the request
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('home:get_quiz'),
            {'category': 'python', 'new_timer': 300}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz_test.html')
        self.assertEqual(response.context['category'], 'python')


class GetQuizViewTestCase(TestCase):
    def test_get_quiz_view(self):
        # Prepare: Create questions and session data
        category = Category.objects.create(category_name='Python')
        question = Question.objects.create(
            category=category,
            question='What does PHP stand for?',
            marks=10,
        )
        response = self.client.get(
            reverse('dashboard:custom_login'),
            context=question
        )
        self.assertEqual(response.status_code, 200)


class SkipQuizViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@ratnaglobaltech.com'
        )
        self.client = Client()
        self.client.login(username='testuser')

    def test_skip_quiz_view(self):
        category = Category.objects.create(category_name='Python')
        suggestion = CourseSuggession.objects.create(
            technology=category,
            course_url='https:python/course',
            difficulty='BG',
            course_name='Python Basics',
            course_instructor='John Doe',
            ratings=4.5,
            course_duration=10.5,
        )
        response = self.client.get(
            reverse('dashboard:custom_login'),
            context=suggestion
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_skip_quiz_view_no_category(self):
        response = self.client.get(reverse('dashboard:custom_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertNotIn('suggestions', response.context)


class SaveTimeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@ratnaglobaltech.com'
        )
        self.client = Client()
        self.client.login(
            username='testuser',
            email='testuser@ratnaglobaltech.com'
        )
        self.session = self.client.session
        self.session['mail'] = 'testuser@ratnaglobaltech.com'
        self.session.save()
        self.url = reverse('home:save_time')

    def test_save_time_success(self):
        data = {
            'current_time': 120,
            'youtube_id': 'vLqTf2b6GZw',
            'percentage': 50,
            'selectedcategory': 'Python',
            'quiz_not': 0,
        }

        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {'message': 'Data saved successfully'}
        )
        # Check if PlayerActivity and QuizUserScore were created/updated
        player_activity = PlayerActivity.objects.get(
            user=self.user,
            youtube_id='vLqTf2b6GZw'
        )
        self.assertEqual(player_activity.current_time, 120)
        self.assertEqual(player_activity.percentage, 50)
        self.assertEqual(player_activity.category, 'Python')

        quiz_user_score = QuizUserScore.objects.get(
            user=self.user,
            quiz_domain='Python'
        )
        self.assertEqual(quiz_user_score.score, 0)
        self.assertFalse(quiz_user_score.is_attempted)

    def test_save_time_exception_handling(self):
        # Simulate an exception being raised in the view
        data = {
            'current_time': 120,
            'youtube_id': 'vLqTf2b6GZw',
            'percentage': 50,
            'selectedcategory': 'Python',
            'quiz_not': 0,
        }
        self.client.session['mail'] = 'testuser@ratnaglobaltech.com'

        # Clear the user session to trigger an exception
        self.client.session.clear()

        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.client.logout()
