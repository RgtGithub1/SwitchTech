from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from home.models import Otp, Video,\
    PlayerActivity, QuizUserScore,\
    Category, CourseSuggession
from .employee import employee_progress, generate_otp, udemy_url, send_otp_mail
from django.utils import timezone
from datetime import timedelta
from django.core import mail


# Employee Logout
class UserLogoutViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser',
                                             email='test@ratnaglobaltech.com')
        # Assuming 'user_logout' is the name of the URL pattern
        self.url = reverse('dashboard:logout')

    def test_user_logout_authenticated(self):
        self.client.login(username='test', email='test@ratnaglobaltech.com')
        response = self.client.get(self.url)
        # Assuming the view redirects after logout
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('mail', self.client.session)
        self.assertNotIn('username', self.client.session)

    def test_user_logout_unauthenticated(self):
        response = self.client.get(self.url)
        # Assuming the view redirects regardless of authentication status
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('mail', self.client.session)
        self.assertNotIn('username', self.client.session)


# Employee Login

class LoginTestCase(TestCase):

    def setUp(self):
        self.user_data = {
            'username': 'Test User',
            'mail': 'test@ratnaglobaltech.com',
        }
        self.user = User.objects.create(
            username=self.user_data['username'],
            email=self.user_data['mail']
        )

    def test_successful_login_existing_user(self):
        user_data1 = {
            'username': 'Test',
            'mail': 'testuser@ratnaglobaltech.com',
        }
        response = self.client.post(reverse('dashboard:custom_login'),
                                    user_data1)
        # Redirect to validate page
        self.assertEqual(response.status_code, 302)

    def test_successful_login_new_user(self):
        new_user_data = {
            'username': 'New User',
            'mail': 'new@ratnaglobaltech.com',
        }
        response = self.client.post(reverse('dashboard:custom_login'),
                                    new_user_data)
        # Redirect to validate page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(
            email=new_user_data['mail']).exists())
        self.assertTrue(Otp.objects.filter(
            mail=new_user_data['mail']).exists())

    def test_invalid_login(self):
        invalid_user_data = {
            'username': 'Invalid User',
            'mail': 'invalid@ratnaglobaltech.com',
        }
        self.assertFalse(User.objects.filter(
            email=invalid_user_data['mail']).exists())
        self.assertFalse(Otp.objects.filter(
            user__email=invalid_user_data['mail']).exists())


# Employee Dashboard
class DashboardPageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
                username='testuser', email='test@ratnaglobaltech.com'
            )
        self.category = Category.objects.create(category_name='Python')

    def test_employee_progress(self):
        # Create required data for PlayerActivity and QuizUserScore
        PlayerActivity.objects.create(user=self.user,
                                      current_time=11255.552,
                                      percentage=50.21,
                                      youtube_id='gkfjhgf',
                                      category=self.category)
        created_at = timezone.now() - timezone.timedelta(days=1)
        QuizUserScore.objects.create(user=self.user,
                                     quiz_domain=self.category,
                                     score=50,
                                     created_at=created_at)
        context = employee_progress(self.user)

        self.assertEqual(context['list_overall_progress'], [50.21])
        self.assertEqual(context['list_categories'], '["Python"]')

    def test_logout_button(self):
        self.client.login(username='Test User',
                          email='test@ratnaglobaltech.com')
        # Replace 'logout' with your actual URL name
        url = reverse('dashboard:logout')
        response = self.client.get(url)
        # Replace 'home' with the actual URL name
        self.assertRedirects(response,
                             expected_url=reverse(
                                 'dashboard:custom_login'))
        self.assertNotIn('_auth_user_id', self.client.session)


# Generate OTP
class GenerateOTPTestCase(TestCase):
    def test_otp_length(self):
        otp = generate_otp()
        self.assertEqual(len(otp), 4,
                         "Generated OTP should have a length of 4")

    def test_otp_digits(self):
        otp = generate_otp()
        for digit in otp:
            self.assertTrue(digit.isdigit(),
                            "Generated OTP should only contain digits")


# send_otp_mail
class SendOtpMailTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_user')
        self.otp_instance = Otp.objects.create(
            mail='test@ratnaglobaltech.com',
            user=self.user,
            otp='1234',
            count=0
        )

    def test_send_otp_mail(self):
        # Clear the outbox before calling the function
        mail.outbox = []

        send_otp_mail('test@ratnaglobaltech.com', 'test_user')

        # Check if the email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'SwitchTech Login-OTP')

        # Check if the OTP instance was updated
        updated_otp_instance = Otp.objects.get(mail='test@ratnaglobaltech.com')
        self.assertEqual(updated_otp_instance.count, 1)

        # Clean up after the test (delete the created objects)
        User.objects.all().delete()
        Otp.objects.all().delete()


class UdemyUrlTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            category_name="Sample Category")
        self.suggestion_beginner = CourseSuggession.objects.create(
            technology=self.category,
            course_url="https://example.com/beginner-course",
            difficulty="BG",
            course_name="Beginner Course",
            course_instructor="Instructor",
            ratings=4.5,
            course_duration=5.5,
        )

        self.suggestion_intermediate = CourseSuggession.objects.create(
            technology=self.category,
            course_url="https://example.com/intermediate-course",
            difficulty="IN",
            course_name="Intermediate Course",
            course_instructor="Instructor",
            ratings=4.0,
            course_duration=7.0,
        )

        self.suggestion_advanced = CourseSuggession.objects.create(
            technology=self.category,
            course_url="https://example.com/advanced-course",
            difficulty="AD",
            course_name="Advanced Course",
            course_instructor="Instructor",
            ratings=4.8,
            course_duration=8.5,
        )

        self.video_python = Video.objects.create(
            title="Test Video python",
            difficulty="BG",
            video_id="xyz123",
            duration=timedelta(hours=1),
            technology_v=self.category,
        )

        self.video_java = Video.objects.create(
            title='Test Video java',
            difficulty='IN',
            video_id='abc123',
            duration=timedelta(hours=1),
            technology_v=self.category
        )
        self.video_oracle = Video.objects.create(
            title='Test Video oracle',
            difficulty='AD',
            video_id='KLM890',
            duration=timedelta(hours=1),
            technology_v=self.category
        )

    def test_udemy_url(self):
        # Test for beginner difficulty
        suggestion_url, course_name, ratings,\
            instructor, duration, difficulty,\
            YouTube_id, Title = udemy_url(30,
                                          self.category)
        self.assertEqual(difficulty, "BG")
        self.assertEqual(course_name, "Beginner Course")
        self.assertEqual(ratings, 4.5)
        self.assertEqual(instructor, "Instructor")
        self.assertEqual(duration, 5.5)
        self.assertEqual(YouTube_id, "xyz123")
        self.assertEqual(Title, "Test Video python")

        # Test for intermediate difficulty
        suggestion_url, course_name, ratings,\
            instructor, duration, difficulty,\
            YouTube_id, Title = udemy_url(60,
                                          self.category)
        self.assertEqual(difficulty, "IN")
        self.assertEqual(course_name, "Intermediate Course")
        self.assertEqual(ratings, 4.0)
        self.assertEqual(instructor, "Instructor")
        self.assertEqual(duration, 7.0)
        self.assertEqual(YouTube_id, "abc123")
        self.assertEqual(Title, "Test Video java")

        # Test for advanced difficulty
        suggestion_url, course_name, ratings,\
            instructor, duration, difficulty,\
            YouTube_id, Title = udemy_url(90,
                                          self.category)
        self.assertEqual(difficulty, "AD")
        self.assertEqual(course_name, "Advanced Course")
        self.assertEqual(ratings, 4.8)
        self.assertEqual(instructor, "Instructor")
        self.assertEqual(duration, 8.5)
        self.assertEqual(YouTube_id, "KLM890")
        self.assertEqual(Title, "Test Video oracle")

    def tearDown(self):
        self.suggestion_beginner.delete()
        self.suggestion_intermediate.delete()
        self.suggestion_advanced.delete()
        self.video_python.delete()
        self.video_java.delete()
        self.video_oracle.delete()
        self.category.delete()


class MyLearningViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()  # Initialize the client
        self.test_user = User.objects.create_user(
            username='testuser',
            email='testuser@ratnaglobaltech.com')
        self.client.force_login(self.test_user)
        self.session = self.client.session
        self.session['mail'] = 'testuser@ratnaglobaltech.com'
        self.session.save()

        self.url = reverse('dashboard:mylearning')

    def test_my_learning_with_learning_modules(self):
        # Create learning modules for the user
        PlayerActivity.objects.create(user=self.test_user,
                                      current_time=100,
                                      youtube_id='vLqTf2b6GZw',
                                      category='python',
                                      is_completed=True)
        PlayerActivity.objects.create(user=self.test_user,
                                      current_time=200,
                                      youtube_id='vLqTf2b6GZw',
                                      category='java',
                                      is_completed=False)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mylearning.html')
        # Check for youtube_id in the response
        self.assertContains(
            response,
            'vLqTf2b6GZw')
        self.assertContains(
            response,
            'python')  # Check for category in the response

    def test_my_learning_no_learning_modules(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mylearning.html')
