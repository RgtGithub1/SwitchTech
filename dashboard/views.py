import logging
import random
import math
from django.contrib.auth.models import User
from home.models import PlayerActivity, Category, \
    Otp, Feedback, QuizUserScore, \
    CourseSuggession, Video
from django.core.mail import send_mail
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
import pytz
from django.http import JsonResponse
from django.contrib import messages


def url(score, category):
    '''
    Based on the employee quiz attempt score and difficulty level
    This will suggest a course from Udemy and youtube course.
    '''
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
        logger.info('Based on employee score we '
                    'are suggesting Beginner course')
        suggesstion = CourseSuggession.objects.filter(
            technology__category_name__icontains=category, difficulty='BG')
        suggestion_vdo = Video.objects.filter(
            technology_v__category_name__icontains=category, difficulty='BG')
        for val in suggesstion:
            logger.info(f'course url : {val}')
            suggesstion_url = val
            course_name = val.course_name
            ratings = val.ratings
            instructor = val.course_instructor
            duration = val.course_duration
            difficulty = val.difficulty
            # logger.info(f'Suggested udemy course: {course_name}')
            break
        for v_id in suggestion_vdo:
            YouTube_id = v_id.video_id
            Title = v_id.title
            # logger.info(f'Suggested youtube course: {Title}')
            # logger.info(f'Youtube ID: {YouTube_id}')
            break

    elif 50 < score <= 70:
        logger.info('Based on employee score we are '
                    'suggesting Intermediate course')
        suggesstion = CourseSuggession.objects.filter(
            technology__category_name__icontains=category, difficulty='IN')
        suggestion_vdo = Video.objects.filter(
            technology_v__category_name__icontains=category, difficulty='IN')
        for val in suggesstion:
            logger.info(f'course url : {val}')
            suggesstion_url = val
            course_name = val.course_name
            ratings = val.ratings
            instructor = val.course_instructor
            duration = val.course_duration
            difficulty = val.difficulty
            logger.info(f'Suggested udemy course: {course_name}')
            break
        for v_id in suggestion_vdo:
            YouTube_id = v_id.video_id
            Title = v_id.title
            logger.info(f'Suggested youtube course: {Title}')
            logger.info(f'Youtube ID: {YouTube_id}')
            break

    elif score > 70 <= 100:
        logger.info('Based on employee score we '
                    'are suggesting Advanced course')
        suggesstion = CourseSuggession.objects.filter(
            technology__category_name__icontains=category, difficulty='AD')
        suggesst_vdo = Video.objects.filter(
            technology_v__category_name__icontains=category, difficulty='AD')
        for val in suggesstion:
            logger.info(f'course url : {val}')
            suggesstion_url = val
            course_name = val.course_name
            ratings = val.ratings
            instructor = val.course_instructor
            duration = val.course_duration
            difficulty = val.difficulty
            logger.info(f'Suggested udemy course: {course_name}')
            break
        for v_id in suggesst_vdo:
            YouTube_id = v_id.video_id
            Title = v_id.title
            logger.info(f'Suggested youtube course: {Title}')
            logger.info(f'Youtube ID: {YouTube_id}')
            break

    return suggesstion_url, course_name, ratings, \
        instructor, duration, difficulty, YouTube_id, Title


logger = logging.getLogger(__name__)

# Create your views here.


def generate_otp():
    '''
    It is will generate an 6 digit random number
    '''
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    logger.info(f'OTP is generated {OTP}')
    return OTP


count = 0


def send_otp_mail(request):
    Employee_Mail = request.session.get('mail')
    username = request.session.get('username')
    print('resend_otp', username)
    print('mail', Employee_Mail)
    user_otp = User.objects.get(username=username)

    otp = generate_otp()
    database = Otp()
    update_count = count + 1
    database.mail = Employee_Mail
    database.otp = otp
    database.user = user_otp
    database.count = update_count

    check = Otp.objects.filter(mail=database.mail)
    if check.count() > 0:
        cc_count = Otp.objects.filter(mail=database.mail). \
            values_list('count', flat=True)
        new_count = list(cc_count)
        new_count1 = new_count[0]
        new_count2 = new_count1 + 1
        logger.warning(f'Previously employee attempted '
                       f'quiz for {new_count1} time')
        Otp.objects.filter(mail=database.mail).update(
            otp=database.otp, user=database.user, count=new_count2)
        logger.info(f'New Otp is sent to employee '
                    f'mail-id: {Employee_Mail}')

        # send_mail(subject="OTP", message=f"Your otp {otp}",
        #           from_email="switchingtechsystem@gmail.com",
        #           recipient_list=[Employee_Mail],
        #           fail_silently=False)

    else:
        print('entering into else part of send_otp_mail')
        logger.info(f'Otp is sent to employee '
                    f'mail-id: {Employee_Mail}')
        send_mail(subject="OTP", message=f"Your otp {otp}",
                  from_email="switchingtechsystem@gmail.com",
                  recipient_list=[Employee_Mail],
                  fail_silently=False)
        database.save()


def loginPage(request):
    '''
    In this method it will check user session is still active or not if active
    it will redirect to Dashboard page, if not it will redirect to login page
    '''

    # del request.session['mail']
    # request.session.save()

    remember_me = request.session.get('remember_me', False)
    print('remember_me is:', remember_me)
    if remember_me:
        logger.info('User session exists (remember me enabled), '
                    'redirecting to the Dashboard page')
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        print('mail is in loginpage:', mail, user)
        overall_progress = PlayerActivity.objects.filter(user=user).order_by(
            '-id').values_list('percentage', 'category')[:3]

        if overall_progress:
            percentages, categories = zip(*overall_progress)
            list_overall_progress = list(percentages)
            list_overall_categories = list(categories)
            rounded_progress = [round(value, 2)
                                for value in list_overall_progress]
            # print(rounded_progress)
            sum_overall_progress = sum(rounded_progress)
            logger.info(f'Employee overall Progress: {sum_overall_progress} %')
            context = {
                'categories': Category.objects.all(),
                'list_overall_progress': rounded_progress,
                'list_categories': list_overall_categories,
                'overall_progress': sum_overall_progress
            }
            logger.info('Dashboard page is accessed')
            # print(context)
            return render(request, 'dashboard.html', context)
        else:
            # Handle the case when no progress data is available
            logger.info('No progress data found')
            context = {
                'categories': Category.objects.all(),
                'list_overall_progress': [],
                'list_categories': [],
                'overall_progress': 0
            }
            return render(request, 'dashboard.html', context)

    elif request.method == "POST":
        logger.info('Login page accessed!')
        if request.POST.get('mail'):
            Employee_Mail = request.POST.get('mail')
            username = request.POST.get('username')
            # created username and mail session
            # to store enter username and mail.
            request.session['username'] = username
            request.session['mail'] = Employee_Mail

            print('mail is in lpost method:', Employee_Mail, username)

            latest_user = User.objects.latest('date_joined')
            last_user_id = int(latest_user.id) if latest_user else 1
            try:
                user = User.objects.get(
                    Q(username__exact=username) | Q(
                        email__exact=Employee_Mail))
                if user.username != username or user.email != Employee_Mail:
                    error_message = 'Invalid username or email.'
                    logger.info('Employee entered invalid username or email')
                    return render(
                        request, 'login.html',
                        {'error_message': error_message})
            except User.DoesNotExist:
                logger.info('New employee details are entered '
                            'and saving into database')
                user = User.objects.create(id=last_user_id + 1,
                                           username=username,
                                           email=Employee_Mail)
                user.save()

            send_otp_mail(request)
            # send_otp_mail(Employee_Mail, username)
            logger.info('Employee details are saved into database')
            logger.info('Employee is redirected to otp validation page!')
            return redirect('dashboard:validate')
    else:
        # logger.error('Employee is not entered valid username or email-id')
        return render(request, 'login.html')


global mail


def validate(request):
    '''
    This method will validate the employee entered otp with their email.
    Once it is validated it will redirect to dashboard page
    '''
    logger.info('OTP validation is accessed!')
    if request.method == 'POST':
        mail = request.POST.get('mail')
        otp = request.POST.get('otp')
        request.session['mail'] = mail
        verified = Otp.objects.filter(mail=mail, otp=otp)
        if verified:
            logger.info('OTP is verified successfully')
            keep_signed_in = request.POST.get('remember_me', False) == 'on'
            logger.info(f'Employee checked keep me signed: {keep_signed_in}')
            user = User.objects.get(email=mail)
            if user is not None:
                login(request, user)
                logger.info('Employee logged-in successfully')
                request.session['username'] = user.username

                if keep_signed_in:
                    # Set session expiration to None
                    request.session.set_expiry(None)
                    request.session['remember_me'] = True
                return redirect('dashboard/')
        else:
            logger.info('Otp is invalid and redirect to login page')
            error_message = 'Invalid OTP. Please try again.'
            return render(request, 'validate.html',
                          {'error_message': error_message})
    else:
        # This handles the GET request,
        # where you might want to display a form for OTP validation
        return render(request, 'validate.html')


def resend_otp(request):
    '''
    This method will resend the OTP to the employee's email.
    '''
    send_otp_mail(request)

    return JsonResponse({'message': 'OTP Re-sent successfully!'})


def dashboard(request):
    '''
    This is the dashboard method where it will
    calculate employee overall progress and generate categories
    '''
    logger.info('Dashboard page is accessed!')
    mail = request.session.get('mail')
    print('mail in dashboard is:', mail)
    user = User.objects.get(email=mail)
    overall_progress = PlayerActivity.objects.filter(user=user).order_by(
        '-id').values_list('percentage', 'category')[:3]

    if overall_progress:
        percentages, categories = zip(*overall_progress)
        list_overall_progress = list(percentages)
        list_overall_categories = list(categories)
        rounded_progress = [round(value, 2) for value in list_overall_progress]
        sum_overall_progress = sum(rounded_progress)
        logger.info(f'Employee overall Progress: {sum_overall_progress} %')
        context = {
            'categories': Category.objects.all(),
            'list_overall_progress': rounded_progress,
            'list_categories': list_overall_categories,
            'overall_progress': sum_overall_progress
        }
        logger.info('Dashboard page is accessed')
        # print(context)
        return render(request, 'dashboard.html', context)
    else:
        # Handle the case when no progress data is available
        logger.info('No progress data found')
        context = {
            'categories': Category.objects.all(),
            'list_overall_progress': [],
            'list_categories': [],
            'overall_progress': 0
        }
        return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def history(request):
    '''
    This method will display the employee previous quiz attempt history
    '''
    logger.info('History page is accessed!')
    mail = request.session.get('mail')
    user = User.objects.get(email=mail)
    score_details = QuizUserScore.objects.filter(
        user=user).order_by('-created_at').values_list(
        'score', 'created_at', 'quiz_domain')[:3]
    user_history = list(score_details)
    if user_history:
        logger.info('Employee previous quiz history present')
        attempts_data = []

        for score, user_time, user_domain in user_history:
            logger.info(f'Employee previous quiz score: {score}')
            user_time = timezone.localtime(
                user_time, timezone=pytz.timezone('Asia/Kolkata'))
            logger.info(f'Employee previous quiz attempt date: {user_time}')
            logger.info(f'Employee previous attempted '
                        f'quiz domain: {user_domain}')

            suggesstion_url, course_name, ratings, \
                instructor, duration, difficulty, \
                YouTube_id, Title = url(score, category=user_domain)

            attempt_data = {
                'user_score': score,
                'user_time': user_time,
                'previous_domain': user_domain,
                'suggestion_url': suggesstion_url,
                'course_name': course_name,
                'ratings': ratings,
                'instructor': instructor,
                'duration': duration,
                'difficulty': difficulty,
                'title': Title
            }
            attempts_data.append(attempt_data)

        return render(request, 'history.html',
                      context={'attempts_data': attempts_data})
    else:
        logger.info('Employee previous quiz history is not present')
        data = {
            'no_data': True  # Add a flag to indicate no data
        }
        return render(request, 'history.html', context=data)


def my_learning(request):
    '''
    This method redirects to my learning page,
    here we can see employee suggested courses.
    '''
    logger.info('My Learning page accessed!')
    mail = request.session.get('mail')
    user = User.objects.get(email=mail)
    retrieve_time = PlayerActivity.objects.filter(
        user=user).order_by('-id').values_list(
        'current_time', 'youtube_id')[0:3]
    resume = list(retrieve_time)
    if resume:
        logger.info('Learning modules are present')
        data = {
            'videos': [{'youtube_id': item[1],
                        'resume_time': item[0]} for item in resume]
        }

        return render(request, 'mylearning.html', context=data)
    else:
        logger.info('Employee doesnt have any learning as of now')
        data = {
            'no_data': True  # Add a flag to indicate no data
        }
        return render(request, 'mylearning.html', context=data)


def feedback(request):
    return render(request, 'feedback.html')


def submit_feedback(request):
    if request.method == 'POST':
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        logger.info('Employee accessed Feedback page')

        q1 = request.POST.get('q1')
        q2 = request.POST.get('q2')
        q3 = request.POST.get('q3')
        q4 = request.POST.get('q4')
        q5 = request.POST.get('q5')
        q6 = request.POST.get('q6')
        q7 = request.POST.get('q7')
        q8 = request.POST.get('q8')
        q9 = request.POST.get('q9')
        q10 = request.POST.get('q10')
        q11 = request.POST.get('q11')
        q12 = request.POST.get('q12')
        q13 = request.POST.get('q13')
        q14 = request.POST.get('q14')
        q15 = request.POST.get('q15')

        user_feedback = Feedback.objects.filter(user=user)

        if user_feedback:
            Feedback.objects.filter(user=user).update(
                overall_exp_with_STS=q1,
                expectation_in_assisting_tech_transition=q2,
                exp_in_navigation_finding_features=q3,
                quiz_engaging_and_interactive=q4,
                quiz_evaluation_of_tech_accuration=q5,
                udm_yt_recom_helpful=q6,
                cs_align_withur_curt_knowledge_levl=q7,
                conveniency_accessing_recom_yt_cs=q8,
                mylearningpage_layout_presentation=q9,
                valueof_progs_tracking_feature_on_dashboard=q10,
                motivate_to_complete_course=q11,
                specific_feature_you_feel_missing=q12,
                how_app_enhanced=q13,
                technical_prob_performance_issue=q14,
                exp_anythingelse_about_STS=q15)
        else:
            add_feedback = Feedback(
                overall_exp_with_STS=q1,
                expectation_in_assisting_tech_transition=q2,
                exp_in_navigation_finding_features=q3,
                quiz_engaging_and_interactive=q4,
                quiz_evaluation_of_tech_accuration=q5,
                udm_yt_recom_helpful=q6,
                cs_align_withur_curt_knowledge_levl=q7,
                conveniency_accessing_recom_yt_cs=q8,
                mylearningpage_layout_presentation=q9,
                valueof_progs_tracking_feature_on_dashboard=q10,
                motivate_to_complete_course=q11,
                specific_feature_you_feel_missing=q12,
                how_app_enhanced=q13,
                technical_prob_performance_issue=q14,
                exp_anythingelse_about_STS=q15, user=user)
            add_feedback.save()
    logger.info('Feedback submitted successfully!')
    messages.success(request, 'Feedback submitted successfully!')

    return redirect('dashboard:dashboard')


def user_logout(request):
    '''
    In this method user will be logout and clear all employee sessions
    '''
    logout(request)
    logger.info('Employee is logged-out successfully!')
    request.session.flush()
    return redirect('/')
