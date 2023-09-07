from home.models import PlayerActivity, Category,\
    CourseSuggession, Video,\
    User, Otp, QuizUserScore
import logging
from django.core.mail import send_mail
import secrets
from django.template.loader import render_to_string
import json
from django.conf import settings


def employee_progress(user):
    '''
    This function will return the overall progress of an employee
    '''
    try:
        overall_progress = PlayerActivity.objects.filter(
            user=user, is_completed=False).order_by(
            '-id').values_list('percentage', 'category')[:3]
        user_attempts = list(
            QuizUserScore.objects.filter(
                user=user).values_list('quiz_domain', flat=True))

        if overall_progress:
            percentages, categories = zip(*overall_progress)
            list_overall_progress = list(percentages)
            list_overall_categories = list(categories)
            rounded_progress = [round(value, 2)
                                for value in list_overall_progress]

            sum_overall_progress = sum(rounded_progress)
            context = {
                'categories': Category.objects.all(),
                'list_overall_progress': rounded_progress,
                'list_categories': json.dumps(list_overall_categories),
                'overall_progress': sum_overall_progress,
                'user_attempts': user_attempts
            }

        else:
            # Handle the case when no progress data is available
            logging.info('No progress data found')
            context = {
                'categories': Category.objects.all(),
                'list_overall_progress': [],
                'list_categories': [],
                'overall_progress': 0,
                'user_attempts': user_attempts
            }
        return context

    except Exception as e:
        logging.error(f"An error occurred in employee_progress: {str(e)}")


def generate_otp():
    '''
    This method will generate 4 digit random number for OTP
    '''
    try:
        OTP = ''.join(secrets.choice("0123456789") for _ in range(4))
        return OTP
    except Exception as e:
        logging.error(f"{e}")


def get_course_suggestion(score, category, difficulty):
    '''
    Based on the employee quiz attempt score, category, and difficulty level,
    this function suggests a course from Udemy and YouTube.
    '''
    suggesstion_url = None
    course_name = None
    ratings = None
    instructor = None
    duration = None
    YouTube_id = None
    Title = None

    try:
        suggesstion = CourseSuggession.objects.filter(
            technology__category_name__icontains=category,
            difficulty=difficulty)
        suggestion_vdo = Video.objects.filter(
            technology_v__category_name__icontains=category,
            difficulty=difficulty)
        for udemy_c in suggesstion:
            suggesstion_url = udemy_c
            course_name = udemy_c.course_name
            ratings = udemy_c.ratings
            instructor = udemy_c.course_instructor
            duration = udemy_c.course_duration
            difficulty = udemy_c.difficulty
            break
        for v_id in suggestion_vdo:
            YouTube_id = v_id.video_id
            Title = v_id.title
            break

    except Exception as e:
        logging.error(f"{e}")

    return suggesstion_url, course_name,\
        ratings, instructor, duration,\
        difficulty, YouTube_id, Title


def udemy_url(score, category):
    '''
    This function returns the URL of the suggested course
    based on employee's result.
    '''
    try:
        if score <= 50:
            return get_course_suggestion(score, category, 'BG')
        elif 50 < score <= 70:
            return get_course_suggestion(score, category, 'IN')
        elif score > 70 <= 100:
            return get_course_suggestion(score, category, 'AD')
    except Exception as e:
        logging.error(f"{e}")


count = 0


def send_otp_mail(Employee_Mail, username):
    '''
    This function sends OTP to Employee Mail ID.
    '''
    try:
        user_otp = User.objects.get(username=username)
        otp = generate_otp()
        # Check if the user already has an OTP record
        database, created = Otp.objects.get_or_create(
            user=user_otp, mail=Employee_Mail)
        if not created:
            # User already has an OTP record, update count and OTP
            database.count += 1
            database.otp = otp
            database.save()
        else:
            # User is new, create a new OTP record
            database.count = 1
            database.otp = otp
            database.save()

        email_template = render_to_string('email.html', {'otp_code': otp})

        send_mail(subject="SwitchTech Login-OTP", message=f"Your OTP: {otp}",
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[Employee_Mail],
                  html_message=email_template,
                  fail_silently=False)
        logging.info("OTP sent to employee mail id")
    except User.DoesNotExist:
        logging.error(f"User with username {username} does not exist.")
    except Exception as e:
        logging.error(f"{e}")
