from django.shortcuts import render, redirect
from  home.models import User, Otp, QuizUserScore
import logging
from django.urls import reverse
from django.db.models import Q
from dashboard.employee import employee_progress, url
from django.utils import timezone
import pytz

# Create your views here.
# @login_required(login_url='login')
def team(request):
    # print('entered into team view function')
    '''
    This method will display the employee previous quiz attempt history
    '''
    logging.info('Team page is accessed!')
    mail = request.session.get('mail')
    print('mail is', mail)
    get_user = Otp.objects.filter(Q(assigned_to=mail) & Q(assigned_status='Approved'))
    assigned_user = [user.user_id for user in get_user]
    print('assigned_user from team', assigned_user)
    user_list = User.objects.filter(id__in=assigned_user)
    print('list_quantity is:', user_list, len(user_list))

    if len(user_list) == 0:
        return render(request, 'team_member.html', {'no_data':True})
    else:
        return render(request, 'team_member.html', {'user_list':user_list})

# @login_required(login_url='login')
def userlist(request):
    # print('entered into team view function')
    '''
    This method will display the employee previous quiz attempt history
    '''
    logging.info('User list page is accessed!')
    mail = request.session.get('mail')

    # fetching active user id.
    active_user = User.objects.filter(email=mail)
    # active_user_id = [active.id for active in active_user]
    active_user_id = [active.id for active in active_user]

    # fetching already assigned user id.
    get_user = Otp.objects.filter(assigned_to=mail)
    assigned_user = [user.user_id for user in get_user]

    # fetching active user manager id.
    active_user_manager = Otp.objects.filter(mail=mail)
    active_user_manager_mail = [user.assigned_to for user in active_user_manager]
    active_user_manager_mail_id = Otp.objects.filter(mail__in=active_user_manager_mail)
    active_user_manager_mail_id = [user.user_id for user in active_user_manager_mail_id]

    # List of user except admin, already assigned user and active user manager.
    assigned_user = assigned_user + [1] + active_user_id + active_user_manager_mail_id
    user_list = User.objects.exclude(id__in=assigned_user)

    if request.method == 'POST':
        id_user = request.POST.get('id_user')
        print('user_id is here', id_user, type(id))
        adding_user = Otp.objects.filter(user_id = int(id_user))
        adding_user.update(assigned_status = 'Pending')
        adding_user.update(assigned_to = mail)
        # logging.info("user assigned")
        return redirect(reverse('manager:userlist'))

    return render(request, 'userlist.html', {'user_list':user_list})

# @login_required(login_url='login')
def notification(request):
    # print('entered into team view function')
    '''
    This method will display the employee previous quiz attempt history
    '''
    # logging.info('notification list page is accessed!')
    mail = request.session.get('mail')
    active_user = Otp.objects.filter(assigned_to=mail)
    active_user_mail = [active.mail for active in active_user]
    print('active mails are:', active_user_mail)

    user_notification = Otp.objects.filter(Q(assigned_to__in=active_user_mail) & Q (assigned_status='Pending'))
    # active_user_mail1 = [active.mail for active in active_user1]
    if user_notification:
        if request.method == 'POST':
            id_user = request.POST.get('id_user')
            cancel = request.POST.get('cancel')
            adding_user = Otp.objects.filter(user_id = int(id_user))
            if cancel:
                adding_user.update(assigned_status = None)
                adding_user.update(assigned_to = None)
            else:
                adding_user.update(assigned_status = "Approved")

            print('user_id is here', id_user, type(id), cancel, type(cancel))
            # logging.info("user assigned")
            return redirect(reverse('manager:notification'))
        else:
            return render(request, 'notification.html', {'user_notification':user_notification})
    else:
        return render(request, 'notification.html', {'no_data':True})


def userdashboard(request):
    print('from userdashboard view', request.GET.get('id'))
    '''
    This is the dashboard method where it will
    calculate employee overall progress and generate categories
    '''
    logging.info('Dashboard page is accessed!')
    
    user_id = request.GET.get('id')
    # fetching user name
    name_user = User.objects.get(id=int(user_id))

    # fetching team details.

    get_use_mail_by_id = Otp.objects.filter(user_id=user_id).values('mail')
    get_use_mail_by_id = [team['mail'] for team in get_use_mail_by_id]
    get_user = Otp.objects.filter(Q(assigned_to=get_use_mail_by_id[0]) & Q(assigned_status='Approved'))
    get_user = [id_user.user_id for id_user in get_user]
    get_user_list = User.objects.filter(id__in=get_user)

    if len(get_user_list) == 0:
        no_data = True
        user_list = get_user_list
    else:
        no_data = False
        user_list = get_user_list

    # fetching history details.
    score_details = QuizUserScore.objects.filter(
            user=name_user).order_by('-created_at').values_list(
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
                history_empty = False
    else:
        history_empty = True
        attempts_data = []



    print('user_id in dashboard is:', user_id, type(user_id))
    # user = User.objects.get(email=mail)
    # user_name = User.objects.filter(id=int(user_id))
    

    # user_name = [name.username for name in user_name]
    context = employee_progress(name_user)
    context['no_data'] = no_data
    context['user_list'] = user_list
    context['user_name'] = str(name_user).capitalize()
    context['history_empty'] = history_empty
    context['attempts_data'] = attempts_data

    return render(request, 'user_dashboard.html', context)
    
