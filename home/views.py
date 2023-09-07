import json
import logging
import random
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Question, QuizUserScore
from .models import PlayerActivity, CourseSuggession, Video
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseBadRequest
from dashboard.employee import udemy_url
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect


def index(request):
    '''
    Instructions page
    '''
    try:
        mail = request.session.get('mail')
        user = User.objects.get(email=mail)
        User_ids = user.id
        user_quiz_attempt_id = QuizUserScore.objects.filter(
            user_id=User_ids).values_list('user_id')
        user_quiz_attempt_count = len(
            [item[0] for item in user_quiz_attempt_id]
        )
        context = {'user_quiz_attempt_count': user_quiz_attempt_count}
        return render(request, 'index.html', context)
    except Exception as e:
        logging.error(f"{e}")


@login_required(login_url='custom_login')
def get_quiz(request):
    '''
    This method will render questions for first
    assessment based on category chosen by user
    '''
    try:
        global category_quiz
        category_quiz = request.GET.get('category')
        if 'quiz_questions' in request.session:
            data = request.session['quiz_questions']
        else:
            questions_objs = Question.objects.all()
            if request.GET.get('category'):
                questions_objs = questions_objs.filter(
                    category__category_name__icontains=request.GET.get(
                        'category'
                    )
                )
            questions_objs = list(questions_objs)
            random.shuffle(questions_objs)
            counter = 0
            data = []
            for question_obj in questions_objs:
                counter += 1
                if counter < 11:
                    data.append({
                        "uid": str(question_obj.uid),
                        "category": question_obj.category.category_name,
                        "question": question_obj.question,
                        "marks": question_obj.marks,
                        "time": request.POST.get('timer'),
                        "answers": question_obj.get_answers()
                    })

            request.session['quiz_questions'] = data
        request.session['quiz_category'] = request.GET.get('category')

        context = {'category': request.GET.get('category'), 'data': data}
        return render(request, 'quiz_test.html', context=context)

    except Exception as e:
        logging.error(e)
        return HttpResponse("Something went wrong")


def calculate_results(request):
    '''
    This method will validate answers and calculate the score
    '''
    try:
        if request.method == 'POST':
            global score, suggesstion_url, course_name, ratings, \
                duration, instructor, difficulty, YouTube_id, Title
            data = request.POST  # Convert POST data to a dictionary
            score = 0
            for question_uid, selected_option in data.items():
                if question_uid != 'csrfmiddlewaretoken':
                    selected_option = selected_option
                    # Remove 'q' prefix and hyphens if 'q' is at the beginning
                    cleaned_question_uid = (
                        question_uid
                        .lstrip('q')
                        .replace('-', '')
                    )
                    is_correct = validate_selected_option(
                        cleaned_question_uid,
                        selected_option
                    )
                    if str(is_correct) == str(selected_option):

                        score += 10

            if 'quiz_questions' in request.session:
                del request.session['quiz_questions']

            mail = request.session.get('mail')
            user = get_object_or_404(User, email=mail)
            category = category_quiz
            score = score
            kolkata_tz = timezone.get_current_timezone()
            current_time = timezone.localtime(timezone.now(), kolkata_tz)
            with transaction.atomic():
                quiz_add, created = QuizUserScore.objects.get_or_create(
                    user=user,
                    quiz_domain=category,
                    defaults={
                        'score': score,
                        'is_attempted': True,
                        'created_at': current_time.astimezone(timezone.utc)
                    }
                )
                if not created:
                    quiz_add.score = score
                    quiz_add.is_attempted = True
                    quiz_add.created_at = current_time.astimezone(timezone.utc)
                    quiz_add.save()
                suggesstion_url, course_name,\
                    ratings, instructor, duration,\
                    difficulty, YouTube_id,\
                    Title = udemy_url(score=quiz_add.score, category=category)
                player, created = PlayerActivity.objects.get_or_create(
                    user=user, category=category,
                    defaults={
                        'current_time': 0,
                        'percentage': 0,
                        'youtube_id': YouTube_id,
                        'is_completed': 0
                    }
                )
                if not created:
                    player.current_time = 0
                    player.percentage = 0
                    player.is_completed = 0
                    player.youtube_id = YouTube_id
                    player.save()
            return redirect('home:final')
    except Exception as e:
        logging.error(f"{e}")
        return JsonResponse({'error': 'Invalid request method'})


def validate_selected_option(question_uid, selected_option):
    '''
    This methis is used to validate the answer given by user is correct or not
    '''
    question = get_object_or_404(Question, uid=question_uid)
    correct_answer = question.question_answer.filter(is_correct=True).first()
    return str(correct_answer)


@login_required(login_url='custom_login')
def final(request):
    '''
    Based on will redirect to results page
    along with the udemy and youtube course data
    '''
    try:
        context = {
            "score": score, 'suggested': suggesstion_url,
            'course_name': course_name, 'ratings': ratings,
            'duration': duration, 'instructor': instructor,
            'difficulty': difficulty, 'YouTube_id': YouTube_id,
            'title': Title}
        return render(request, 'results.html', context=context)
    except Exception as e:
        logging.error(f"{e}")
        return JsonResponse({'message': 'data not saved'})


@login_required(login_url='custom_login')
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
            video_data = [
                (video.video_id, video.title, video.difficulty)
                for video in videos
            ]
            context = {
                'suggestions': suggestions,
                'video_data': video_data,
                'selected_category': selected_category
            }
        logging.info('Employee skipped the quiz')
        return render(request, 'skipquiz.html', context)
    except Exception as e:
        logging.error(f"this is message {e}")


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
                # quiz.created_at = datetime.now()
                quiz.created_at = timezone.now()
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
            return JsonResponse({'message': 'Data saved successfully'})
        else:
            return HttpResponseBadRequest('Invalid request method')
    except Exception as e:
        logging.error(f"{e}")
