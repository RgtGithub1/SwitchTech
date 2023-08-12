from home.models import PlayerActivity, Category, CourseSuggession, Video, User, Otp, QuizUserScore
import logging
import random
import math
from django.core.mail import send_mail


def employee_progress(user):
    overall_progress = PlayerActivity.objects.filter(user=user, is_completed=False).order_by(
            '-id').values_list('percentage', 'category')[:3]
    
    if overall_progress:
                percentages, categories = zip(*overall_progress)
                list_overall_progress = list(percentages)
                list_overall_categories = list(categories)
                rounded_progress = [round(value, 2)
                                    for value in list_overall_progress]
                # print(rounded_progress)
                sum_overall_progress = sum(rounded_progress)
                user_attempts = list(QuizUserScore.objects.filter(user=user).values_list('quiz_domain', flat=True))
                logging.info('Employee already attempted these quizzes: %s, this categories are disabled', user_attempts)
                logging.info(f'Employee'
                             f' overall Progress: {sum_overall_progress} %')
                
                # User_ids = user.id

                # user_quiz_attempt_id = QuizUserScore.objects.filter(user_id=User_ids).values_list('user_id')

                # user_quiz_attempt_count = len([item[0] for item in user_quiz_attempt_id])
                
                context = {
                    'categories': Category.objects.all(),
                    'list_overall_progress': rounded_progress,
                    'list_categories': list_overall_categories,
                    'overall_progress': sum_overall_progress,
                    'user_attempts':user_attempts
                    # 'user_quiz_attempt_count': user_quiz_attempt_count
                }
                logging.info('Dashboard page is accessed')
                # print(context)
    else:
                # Handle the case when no progress data is available
                logging.info('No progress data found')
                context = {
                    'categories': Category.objects.all(),
                    'list_overall_progress': [],
                    'list_categories': [],
                    'overall_progress': 0,
                    'user_attempts':[]
                    # 'user_quiz_attempt_count': []
                }
    return context

def generate_otp():
    try:
        '''
        It is will generate an 6 digit random number
        '''
        OTP = ''
        digits = "0123456789"
        for i in range(4):
            OTP += digits[math.floor(random.random() * 10)]
        logging.info(f'OTP is generated {OTP}')
        print('OTP is: ', OTP)
        return OTP
    except Exception as e:
        logging.error(f"{e}")

def url(score, category):
    '''
    Based on the employee quiz attempt score and difficulty level
    This will suggest a course from Udemy and youtube course.
    '''
    try:
        YouTube_id = ''
        Title = ''
        suggesstion_url = None
        course_name = None
        ratings = None
        instructor = None
        duration = None
        difficulty = None
        YouTube_id = None
        Title = None

        if score <= 50:
            logging.info('Based on employee score we'
                         ' are suggesting Beginner course')
            suggesstion = CourseSuggession.objects.filter(
                technology__category_name__icontains=category,
                difficulty='BG')
            suggestion_vdo = Video.objects.filter(
                technology_v__category_name__icontains=category,
                difficulty='BG')
            for val in suggesstion:
                logging.info(f'course url : {val}')
                suggesstion_url = val
                course_name = val.course_name
                ratings = val.ratings
                instructor = val.course_instructor
                duration = val.course_duration
                difficulty = val.difficulty
                break
            for v_id in suggestion_vdo:
                YouTube_id = v_id.video_id
                Title = v_id.title
                break

        elif 50 < score <= 70:
            logging.info('Based on employee score we are'
                         ' suggesting Intermediate course')
            suggesstion = CourseSuggession.objects.filter(
                technology__category_name__icontains=category,
                difficulty='IN')
            suggestion_vdo = Video.objects.filter(
                technology_v__category_name__icontains=category,
                difficulty='IN')
            for val in suggesstion:
                logging.info(f'course url : {val}')
                suggesstion_url = val
                course_name = val.course_name
                ratings = val.ratings
                instructor = val.course_instructor
                duration = val.course_duration
                difficulty = val.difficulty
                logging.info(f'Suggested udemy course: {course_name}')
                break
            for v_id in suggestion_vdo:
                YouTube_id = v_id.video_id
                Title = v_id.title
                logging.info(f'Suggested youtube course: {Title}')
                logging.info(f'Youtube ID: {YouTube_id}')
                break

        elif score > 70 <= 100:
            logging.info('Based on employee score we'
                         ' are suggesting Advanced course')
            suggesstion = CourseSuggession.objects.filter(
                technology__category_name__icontains=category,
                difficulty='AD')
            suggesst_vdo = Video.objects.filter(
                technology_v__category_name__icontains=category,
                difficulty='AD')
            for val in suggesstion:
                logging.info(f'course url : {val}')
                suggesstion_url = val
                course_name = val.course_name
                ratings = val.ratings
                instructor = val.course_instructor
                duration = val.course_duration
                difficulty = val.difficulty
                logging.info(f'Suggested udemy course: {course_name}')
                break
            for v_id in suggesst_vdo:
                YouTube_id = v_id.video_id
                Title = v_id.title
                logging.info(f'Suggested youtube course: {Title}')
                logging.info(f'Youtube ID: {YouTube_id}')
                break

        return suggesstion_url, course_name, ratings, \
            instructor, duration, difficulty, YouTube_id, Title
    except Exception as e:
        logging.error(f"{e}")


count = 0

def send_otp_mail(Employee_Mail, username):
    try:
        Employee_Mail = Employee_Mail
        username = username
        user_otp = User.objects.get(username=username)
        print('user_otp is :', user_otp)
        otp = generate_otp()
        database = Otp()
        update_count = count + 1
        database.mail = Employee_Mail
        database.otp = otp
        database.user = user_otp  
        database.count = update_count

        print('details: ', otp, update_count, Employee_Mail, username)


        check = Otp.objects.filter(mail=database.mail)
        print('check is enter email is there or not', check)
        if check.count() > 0:
            cc_count = Otp.objects.filter(mail=database.mail). \
                values_list('count', flat=True)
            new_count = list(cc_count)
            new_count1 = new_count[0]
            new_count2 = new_count1 + 1

            Otp.objects.filter(mail=database.mail).update(
                otp=database.otp, user=database.user, count=new_count2)
            send_mail(subject="OTP", message=f"Your otp {otp}",
                      from_email="switchingtechsystem@gmail.com",
                      recipient_list=[Employee_Mail],
                      fail_silently=False)
            logging.info(f'Otp sent to registered employee'
                         f' mail-id: {Employee_Mail} Otp: {otp}')
        else:
            send_mail(subject="OTP", message=f"Your otp {otp}",
                      from_email="switchingtechsystem@gmail.com",
                      recipient_list=[Employee_Mail],
                      fail_silently=False)
            database.save()
            logging.info(f'Otp sent to new register employee'
                         f' mail-id: {Employee_Mail} Otp: {otp}')
    except Exception as e:
        logging.error(f"{e}")
