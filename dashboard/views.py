import logging
from django.contrib.auth.models import User, AbstractUser, AbstractBaseUser
from home.models import PlayerActivity, Category, \
    Otp, Feedback, QuizUserScore
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
import pytz
from django.http import JsonResponse
from django.contrib import messages
from .employee import employee_progress, generate_otp, url, send_otp_mail
from django.urls import reverse

# Create your views here.

def loginPage(request):
    '''
    In this method it will check user session is still active or not if active
    it will redirect to Dashboard page, if not it will redirect to login page
    '''

    # del request.session['mail']
    # request.session.save()
    try:
        logging.basicConfig(filename='logs.log',
                            level=logging.INFO,
                            format='%(filename)s:%(lineno)d - %(asctime)s -'
                                   ' %(levelname)s - %(message)s')
        # remember session created.
        remember_me = request.session.get('remember_me', False)
        # logging.info(f'remember_me is: {remember_me}')
        if remember_me:
            logging.info('User session exists (remember me enabled),'
                         ' redirecting to the Dashboard page')
            mail = request.session.get('mail')
            user = User.objects.get(email=mail)
            print('mail is in loginpage:', mail, user)
            context = employee_progress(user)
            return render(request, 'dashboard.html', context)
        else:
            if request.method == "POST":
                Employee_Mail = request.POST.get('mail')
                username = request.POST.get('username')
                print('in login page', Employee_Mail, username)
                request.session['username'] = username
                request.session['mail'] = Employee_Mail
                latest_user = User.objects.latest('date_joined')
                last_user_id = int(latest_user.id) if latest_user else 1
                print('latest user id is', last_user_id)
                try:
                    user = User.objects.get(
                        Q(username__exact=username) | Q(
                            email__exact=Employee_Mail))
                    if user.username != username \
                            or user.email != Employee_Mail:
                        error_message = 'Invalid username or email.'
                        messages.error(request, error_message)
                        logging.info('Employee entered'
                                     ' invalid username or email')
                        return redirect(reverse('dashboard:login'))
                except User.DoesNotExist:
                    logging.info('New employee details are entered'
                                 ' and saving into database')
                    user = User.objects.create(id=last_user_id + 1,
                                               username=username,
                                               email=Employee_Mail)
                    user.save()

                send_otp_mail(Employee_Mail, username)
                logging.info('Employee details are saved into database')
                logging.info('Employee is redirected to otp validation page!')

                return redirect(reverse('dashboard:validate'))
            
            return render(request, 'login.html')
    except Exception as e:
        logging.error(f"{e}")


def validate(request):
    '''
    This method will validate the employee entered otp with their email.
    Once it is validated it will redirect to dashboard page
    '''
    try:

        logging.info('OTP validation is accessed!')
        if request.method == 'POST':
            mail = request.POST.get('mail')
            otp = request.POST.get('otp')
            request.session['mail'] = mail
            verified = Otp.objects.filter(mail=mail, otp=otp)
            if verified:
                logging.info('OTP is verified successfully')
                keep_signed_in = request.POST.get('remember_me', False) == 'on'
                logging.info(f'Employee checked keep me signed:'
                             f' {keep_signed_in}')
                user = User.objects.get(email=mail)
                if user is not None:
                    login(request, user)
                    logging.info('Employee logged-in successfully')
                    request.session['username'] = user.username

                    if keep_signed_in:
                        # Set session expiration to None
                        request.session.set_expiry(None)
                        request.session['remember_me'] = True
                    return redirect('dashboard/')
            else:
                logging.info('Otp is invalid and redirect to login page')
                error_message = 'Invalid OTP. Please try again.'
                messages.error(request, error_message)
                return redirect(reverse('dashboard:validate'))

        else:
            # This handles the GET request,
            # where you might want to display a form for OTP validation
            return render(request, 'validate.html')
    except Exception as e:
        logging.error(f"{e}")



def resend_otp(request):
    '''
    This method will resend the OTP to the employee's email.
    '''

    try:
        username = request.session.get('username')
        Employee_Mail = request.session.get('mail')
        print('resend otp to mail is', username, Employee_Mail)
        send_otp_mail(Employee_Mail, username)
        logging.info('OTP resened to mail')
        return JsonResponse({'message': 'OTP Re-sent successfully!'})
    except Exception as e:
        logging.error(f"{e}")



def dashboard(request):
    '''
    This is the dashboard method where it will
    calculate employee overall progress and generate categories
    '''
    try:
        logging.info('Dashboard page is accessed!')
        mail = request.session.get('mail')
        print('mail in dashboard is:', mail)
        user = User.objects.get(email=mail)
        print('diplaying progress report in dashboard page', user)

        context = employee_progress(user)
        return render(request, 'dashboard.html', context)
    except Exception as e:
        logging.error(f"{e}")



@login_required(login_url='login')
def history(request):
    '''
    This method will display the employee previous quiz attempt history
    '''
    try:

        logging.info('History page is accessed!')
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        score_details = QuizUserScore.objects.filter(
            user=user).order_by('-created_at').values_list(
            'score', 'created_at', 'quiz_domain')[:3]
        user_history = list(score_details)
        if user_history:
            logging.info('Employee previous quiz history present')
            attempts_data = []

            for score, user_time, user_domain in user_history:
                logging.info(f'Employee previous quiz score: {score}')
                user_time = timezone.localtime(
                    user_time, timezone=pytz.timezone('Asia/Kolkata'))
                logging.info(f'Employee previous quiz attempt date:'
                             f' {user_time}')
                logging.info(f'Employee previous attempted'
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
            logging.info('Employee previous quiz history is not present')
            data = {
                'no_data': True  # Add a flag to indicate no data
            }
            return render(request, 'history.html', context=data)
    except Exception as e:
        logging.error(f"{e}")



def my_learning(request):
    '''
    This method redirects to my learning page,
    here we can see employee suggested courses.
    '''
    try:
        logging.info('My Learning page accessed!')
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        retrieve_time = PlayerActivity.objects.filter(
            user=user).order_by('-id').values_list(
            'current_time', 'youtube_id')[0:3]
        resume = list(retrieve_time)
        if resume:
            logging.info('Learning modules are present')
            data = {
                'videos': [{'youtube_id': item[1],
                            'resume_time': item[0]} for item in resume]
            }

            return render(request, 'mylearning.html', context=data)
        else:
            logging.info('Employee doesnt have any learning as of now')
            data = {
                'no_data': True  # Add a flag to indicate no data
            }
            return render(request, 'mylearning.html', context=data)
    except Exception as e:
        logging.error(f"{e}")


def feedback(request):
    try:
        logging.info('Feed back page accessed')
        return render(request, 'feedback.html')
    except Exception as e:
        logging.error(f"{e}")


def submit_feedback(request):
    try:
        if request.method == 'POST':
            mail = request.session.get('mail')
            user = User.objects.get(email=mail)
            logging.info('Employee accessed Feedback page')

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
        logging.info('Feedback submitted successfully!')
        messages.success(request, 'Feedback submitted successfully!')

        return redirect('dashboard:dashboard')
    except Exception as e:
        logging.error(f"{e}")


def user_logout(request):
    '''
    In this method user will be logout and clear all employee sessions
    '''
    try:
        logout(request)
        logging.info('Employee is logged-out successfully!')
        request.session.flush()
        return redirect('/')
    except Exception as e:
        logging.error(f"{e}")

