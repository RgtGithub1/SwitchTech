import json
import logging
import random
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Question, QuizAttempt, QuizUserScore
from .models import PlayerActivity, CourseSuggession, Video
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseBadRequest
from dashboard.employee import url
from datetime import datetime
from django.db import transaction
from django.shortcuts import get_object_or_404



def index(request):
    # '''
    # Instructions page
    # '''
    # try:
    #     logging.info('Instruction page is accessed')
    #     return render(request, 'index.html')
    # except Exception as e:
    #     logging.error(f"{e}")
    '''
    Instructions page
    '''
    try:
        # logging.info('Instruction page is accessed')
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        User_ids = user.id
        user_quiz_attempt_id = QuizUserScore.objects.filter(user_id=User_ids).values_list('user_id')
        user_quiz_attempt_count = len([item[0] for item in user_quiz_attempt_id])
        context = {'user_quiz_attempt_count': user_quiz_attempt_count}
        return render(request, 'index.html', context)
    except Exception as e:
        logging.error(f"{e}")


@login_required(login_url='login')
def quiz(request):
    '''
    Based on the selected category it will redirect to quiz page
    '''
    try:
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        time_remaining = QuizAttempt.objects.filter(
            user=user).values_list('timer', 'domain')
        if time_remaining:
            rem_time = list(time_remaining)
            update_timer = rem_time[0][0]
            logging.info(f'Employee still having'
                         f' the previous quiz timer with {update_timer} sec')
            if request.GET.get('category') == \
                    rem_time[0][1] and rem_time[0][0] > 5:
                new_timer = update_timer
            else:
                new_timer = 300
        else:
            new_timer = 300
        context = {'category': request.GET.get('category'),
                   'new_timer': new_timer}

        
        logging.info('Employee agreed to terms and conditions with selected'
                     ' domain {}, redirecting to quiz page'.
                     format(request.GET.get('category')))
        return render(request, 'quiz.html', context)
    except Exception as e:
        logging.error(f"{e}")


@login_required(login_url='login')
def get_quiz(request):
    '''
    Based on selected category it will generate
    ten random questions along with options
    '''
    # print('get quiz based on category:', request.GET.get('category'))
    try:
        logging.info('Quiz question loaded successfully')
        questions_objs = Question.objects.all()
        if request.GET.get('category'):
            # print('enter into category domain')
            request.session['category'] = request.GET.get('category')
            # print('storing in session category:', request.GET.get('category'), type(request.GET.get('category')))
            questions_objs = questions_objs.filter(
                category__category_name__icontains=request.GET.get('category'))
            # print('filtered questions', questions_objs)
        questions_objs = list(questions_objs)
        # print('list of questions:', questions_objs)
        data = []
        random.shuffle(questions_objs)
        counter = int()
        for question_obj in questions_objs:
            counter += 1
            if counter < 11:
                data.append({
                    "uid": question_obj.uid,
                    "category": question_obj.category.category_name,
                    "question": question_obj.question,
                    "marks": question_obj.marks,
                    "time": request.POST.get('timer'),
                    "answers": question_obj.get_answers()
                })
    
        return JsonResponse({'data': data, 'status': True})
    
    except Exception as e:
        logging.error(e)
    return HttpResponse("Something went worng")


@login_required(login_url='login')
def save_remaining_time(request):
    '''
    This method is used to save the remaining quiz timer in database
    '''
    try:
        if request.method == 'POST':
            remaining_time = request.POST.get('remainingTime')
            category = request.POST.get('category')
            quiz_timer = QuizAttempt()
            mail = request.session.get('mail')
            user = User.objects.get(email=mail)
            quiz_timer.timer = remaining_time
            quiz_timer.user = user
            quiz_timer.domain = category
            quiz_timer.save()
            logging.info(f'saving remaining'
                         f' time in database: {remaining_time}')
            return JsonResponse(
                {'message': 'Remaining time saved successfully'})
        return JsonResponse({'message': 'Invalid request method'}, status=400)
    except Exception as e:
        logging.error(f"{e}")


@login_required(login_url='login')
def result(request):
    '''
    This method will generate employee score
    '''
    try:
        if request.method == 'POST':
            logging.info('Results page accessed!')

            global score, suggesstion_url, course_name, ratings, \
                duration, instructor, difficulty, YouTube_id, Title
            
            mail = request.session.get('mail')
            user = get_object_or_404(User, email=mail)
            
            score_data = json.loads(request.body)
            score = score_data.get('score')
            category = score_data.get('category')
            
            kolkata_tz = timezone.get_current_timezone()
            current_time = timezone.localtime(timezone.now(), kolkata_tz)
            
            with transaction.atomic():
                quiz_add, created = QuizUserScore.objects.get_or_create(
                    user=user, quiz_domain=category,
                    defaults={'score': score * 10, 'is_attempted': True, 'created_at': current_time.astimezone(timezone.utc)}
                )
                
                if not created:
                    quiz_add.score = score * 10
                    quiz_add.is_attempted = True
                    quiz_add.created_at = current_time.astimezone(timezone.utc)
                    quiz_add.save()
                
                suggesstion_url, course_name, ratings, instructor, duration, difficulty, YouTube_id, Title = url(score=quiz_add.score, category=category)
                
                player, created = PlayerActivity.objects.get_or_create(
                    user=user, category=category,
                    defaults={'current_time': 0, 'percentage': 0, 'youtube_id': YouTube_id, 'is_completed': 0}
                )
                
                if not created:
                    player.current_time = 0
                    player.percentage = 0
                    # player.category = category
                    player.is_completed = 0
                    player.youtube_id = YouTube_id
                    player.save()
                
            logging.info(f'Based on quiz attempt, employee got {score * 10} score & selected domain {category}')
            
            return HttpResponse(status=200)
    except Exception as e:
        logging.error(f"An error occurred in the result method: {str(e)}")


@login_required(login_url='login')
def skip_quiz(request):
    '''
    This method will skip the quiz and redirect to overall
    recomendations page based on selected catergory
    '''
    try:
        selected_category = request.GET.get('category')
        context = {}
        if selected_category:
            suggestions = CourseSuggession.objects.filter(
                technology__category_name__icontains=selected_category)
            
            videos = Video.objects.filter(
                technology_v__category_name__icontains=selected_category)
    
            video_data = [(video.video_id, video.title, video.difficulty) for video in videos]
            
            context = {
                'suggestions': suggestions,
                'video_data': video_data,
                'selected_category':selected_category
            }
        logging.info('Employee skipped the quiz and select domain'
                     ' {} and redirected to all recomendations page'
                     ' with all the avaliable courses'.
                     format(request.GET.get('category')))
        return render(request, 'skipquiz.html', context)
    except Exception as e:
        logging.error(f"this is message {e}")


@login_required(login_url='login')
def final(request):
    '''
    Based on will redirect to results page
    along with the udemy and youtube course data
    '''
    try:
        context = {
            "score": score * 10, 'suggested': suggesstion_url,
            'course_name': course_name, 'ratings': ratings,
            'duration': duration, 'instructor': instructor,
            'difficulty': difficulty, 'YouTube_id': YouTube_id,
            'title': Title}
        logging.info('Employee redirect'
                     ' to results page with course suggestion')
        return render(request, 'results.html', context=context)
    except Exception as e:
        logging.error(f"{e}")


@csrf_exempt
def save_time(request):
    '''
    This method is used to record the duration
    of completed time for a YouTube video
    '''
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            current_time = data.get('current_time')
            youtube_id = data.get('youtube_id')
            percentage = data.get('percentage')
            selectedcategory = data.get('selectedcategory')
            quiz_not = data.get('quiz_not')
            if current_time is None:
                current_time = 0  # Assign a numeric default value

            mail = request.session.get('mail')
            user = User.objects.get(email=mail)
            check = PlayerActivity.objects.filter(
                youtube_id=youtube_id, user=user)
            if quiz_not == 0:
                quiz = QuizUserScore()
                quiz.user = user
                quiz.quiz_domain = selectedcategory
                quiz.score = 0
                # kolkata_tz = timezone.get_current_timezone()
                # current_time = timezone.localtime(timezone.now(), kolkata_tz)
                # quiz.created_at = current_time.astimezone(timezone.utc)
                quiz.created_at = datetime.now()
                quiz.is_attempted = False
                quiz.save()
            if check:
                PlayerActivity.objects.filter(
                    user=user, youtube_id=youtube_id).update(
                    current_time=current_time, percentage=percentage)
               
            else:
                PlayerActivity.objects.create(current_time=current_time,
                                              percentage=percentage,
                                              youtube_id=youtube_id,
                                              category=selectedcategory,
                                              user=user)
                
            logging.info(f'Watched timer for youtube id:'
                         f' {youtube_id} with percentage : {percentage}')
            return JsonResponse({'message': 'Data saved successfully'})
        else:
            return HttpResponseBadRequest('Invalid request method')
    except Exception as e:
        logging.error(f"{e}")
