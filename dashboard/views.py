import logging
from django.contrib.auth.models import User
from home.models import PlayerActivity, \
    Otp, Feedback, QuizUserScore
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
import pytz
from django.http import JsonResponse
from django.contrib import messages
from .employee import employee_progress, udemy_url, send_otp_mail
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def loginPage(request):
    '''
    In this method it will check user session is still active or not if active
    it will redirect to Dashboard page, if not it will redirect to login page
    '''
    try:
        logging.basicConfig(filename='logs.log',
                            level=logging.INFO,
                            format='%(module)s.%(funcName)s:%(lineno)d - '
                                   '%(asctime)s - %(levelname)s - %(message)s')
        remember_me = request.session.get('remember_me', False)
        if remember_me:

            if 'quiz_questions' in request.session:
                del request.session['quiz_questions']
            mail = request.session.get('mail')
            user = User.objects.get(email=mail)
            context = employee_progress(user)
            return render(request, 'dashboard.html', context)
        else:
            if request.method == "POST":
                Employee_Mail = request.POST.get('mail')
                username = Employee_Mail.split('@')[0]
                request.session['username'] = username
                request.session['mail'] = Employee_Mail
                latest_user = User.objects.latest('date_joined')
                last_user_id = int(latest_user.id) if latest_user else 1
                try:
                    user = User.objects.get(
                         Q(email__exact=Employee_Mail))
                    if user.email != Employee_Mail:
                        error_message = 'Invalid username or email.'
                        messages.error(request, error_message)
                        logging.info('Employee entered'
                                     ' invalid username or email')
                        return redirect(reverse('dashboard:login'))
                except User.DoesNotExist:
                    user = User.objects.create(id=last_user_id + 1,
                                               username=username,
                                               email=Employee_Mail)
                    user.save()
                send_otp_mail(Employee_Mail, username)
                return redirect(reverse('dashboard:validate'))
            return render(request, 'login.html')
    except Exception as e:
        logging.error(f"{e}")


def validate_otp(request):
    '''
    This method will validate the employee entered otp with their email.
    Once it is validated it will redirect to dashboard page
    '''
    try:
        if request.method == 'POST':
            mail = request.POST.get('mail')
            otp = request.POST.get('otp')
            request.session['mail'] = mail
            verified = Otp.objects.filter(mail=mail, otp=otp)
            if verified:
                keep_signed_in = request.POST.get('remember_me', False) == 'on'
                user = User.objects.get(email=mail)
                if user is not None:
                    login(request, user)
                    logging.info('OTP is verified and logged-in successfully')
                    request.session['username'] = user.username

                    if keep_signed_in:
                        request.session.set_expiry(None)
                        request.session['remember_me'] = True
                    return redirect('dashboard/')
            else:
                logging.info('Invalid OTP. Please try again')
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
        send_otp_mail(Employee_Mail, username)
        logging.info('OTP re-sended to employee mail-ID')
        return JsonResponse({'message': 'OTP Re-sent successfully!'})
    except Exception as e:
        logging.error(f"{e}")


def dashboard(request):
    '''
    This is the dashboard method where it will
    calculate employee overall progress and generate categories
    '''
    try:
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        context = employee_progress(user)
        return render(request, 'dashboard.html', context)
    except Exception as e:
        logging.error(f"{e}")


@login_required(login_url='custom_login')
def history(request):
    '''
    This method will display the employee previous quiz attempt history
    '''
    try:
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        score_details = QuizUserScore.objects.filter(
            user=user).order_by('-created_at').values_list(
            'score', 'created_at', 'quiz_domain', 'is_attempted')[:3]
        user_history = list(score_details)

        if user_history:
            attempts_data = []

            for score, user_time, user_domain, is_attempted in user_history:
                user_time = timezone.localtime(
                    user_time, timezone=pytz.timezone('Asia/Kolkata'))
                attempt = is_attempted

                suggesstion_url, course_name, ratings, \
                    instructor, duration, difficulty, \
                    YouTube_id, Title = udemy_url(score, category=user_domain)

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
                    'title': Title,
                    'attempt': attempt
                }

                attempts_data.append(attempt_data)
            return render(request, 'history.html',
                          context={'attempts_data': attempts_data})
        else:
            data = {
                'no_data': True  # Add a flag to indicate no data
            }
            return render(request, 'history.html', context=data)
    except Exception as e:
        logging.error(f"{e}")
        return HttpResponse("An error occurred while processing the request.")


def my_learning(request):
    '''
    This method redirects to my learning page,
    here we can see employee suggested courses.
    '''
    try:
        # reassessment refresh session dump
        if 'selected_question_ids' in request.session:
            del request.session['selected_question_ids']

        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        retrieve_time = PlayerActivity.objects.filter(
            user=user).order_by('-id').values_list(
            'current_time',
            'youtube_id',
            'category',
            'is_completed')[0:3]
        resume = list(retrieve_time)
        if resume:
            data = {
                'videos': [{'youtube_id': item[1],
                            'resume_time': item[0],
                            'category':item[2],
                            'status':item[3]} for item in resume]
            }

            return render(request, 'mylearning.html', context=data)
        else:
            data = {
                'no_data': True  # Add a flag to indicate no data
            }
            return render(request, 'mylearning.html', context=data)

    except Exception as e:
        logging.error(f"{e}")


def resendfeedback(request):
    '''
        if user has already submitted feedback
    and again he want to submit the feedback,
    this method will be called
    '''
    try:
        return render(request, 'feedback.html')
    except Exception as e:
        logging.error(f"{e}")


def feedback(request):
    '''
    This method will check whether feedback has
    been submitted previously or not depending on that it will
    render the html page
    '''
    try:
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        data = Feedback.objects.filter(user=user)
        if data.count() >= 1:
            data_count = True
            return render(request, 'thank_you.html')
        else:
            data_count = None
            return render(request, 'feedback.html', {'data_count': data_count})
    except Exception as e:
        logging.error(f"{e}")


def submit_feedback(request):
    '''
        This method will store the user input in Feedback table
    '''
    try:
        if request.method == 'POST':
            mail = request.session.get('mail')
            user = User.objects.get(email=mail)
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
            user_feedback = Feedback.objects.filter(user=user)
            if user_feedback:
                Feedback.objects.filter(user=user).update(
                    overall_exp_with_STS=q1,
                    expectation_in_assisting_tech_transition=q2,
                    udm_yt_recom_helpful=q3,
                    cs_align_withur_curt_knowledge_levl=q4,
                    conveniency_accessing_recom_yt_cs=q5,
                    valueof_progs_tracking_feature_on_dashboard=q6,
                    motivate_to_complete_course=q7,
                    specific_feature_you_feel_missing=q8,
                    how_app_enhanced=q9,
                    technical_prob_performance_issue=q10)

            else:
                add_feedback = Feedback(
                    overall_exp_with_STS=q1,
                    expectation_in_assisting_tech_transition=q2,
                    udm_yt_recom_helpful=q3,
                    cs_align_withur_curt_knowledge_levl=q4,
                    conveniency_accessing_recom_yt_cs=q5,
                    valueof_progs_tracking_feature_on_dashboard=q6,
                    motivate_to_complete_course=q7,
                    specific_feature_you_feel_missing=q8,
                    how_app_enhanced=q9,
                    technical_prob_performance_issue=q10, user=user)
                add_feedback.save()
        logging.info('Feedback submitted successfully!')
        messages.success(request, 'Feedback submitted successfully!')
        return redirect('dashboard:dashboard')
    except Exception as e:
        logging.error(f"{e}")


def user_logout(request):
    '''
    In this method user will be logout
    and clear the particular application sessions
    '''
    try:
        # Clear specific session variables for your application
        if 'mail' in request.session:
            del request.session['mail']
        if 'username' in request.session:
            del request.session['username']
        logout(request)
        logging.info('Employee is logged-out successfully!')
        return redirect('/')
    except Exception as e:
        logging.error(f"{e}")


@csrf_exempt  # Disable CSRF protection for demonstration purposes; use appropriate protection in production
def update_completion_status(request):
    '''
    This method will update completion status of video in PlayerActivity table when user has completely watched the video
    '''
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        try:
            activity = PlayerActivity.objects.get(user=user,youtube_id=video_id)
            activity.is_completed = True
            activity.save()
            return JsonResponse({'message': 'Completion status updated successfully'})
        except PlayerActivity.DoesNotExist:
            return JsonResponse({'message': 'Video not found'}, status=404)
    return JsonResponse({'message': 'Invalid request'}, status=400)