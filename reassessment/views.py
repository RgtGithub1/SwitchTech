from django.shortcuts import render
from .models import QuizQuestion, FinalQuizAnswer
from django.contrib.auth.models import User
from home.models import PlayerActivity
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import logging
from django.http import HttpResponse
import random
from home.models import Video
import uuid


# Create your views here.
def quiz_page(request):
    try:
        category = request.GET.get('category')
        print('categoryaaaaaaaaaaa:', category)
        video_id_datas = request.GET.get('video_id_data')
        print('video_id_datas:', video_id_datas)

        difficulty_level = list(Video.objects.filter(video_id=video_id_datas).values('difficulty'))
        difficulty_level_id = [video['difficulty'] for video in difficulty_level]
        difficulty_level_data = difficulty_level_id[0]
        print('difficulty_level_data:', difficulty_level_data)

        selected_question_ids = request.session.get('selected_question_ids')
        print('selected_question_ids:', selected_question_ids)

        if selected_question_ids is None:
            num_questions_to_display = 2
            questions = list(QuizQuestion.objects.filter(Technology__category_name=category, difficulty=difficulty_level_data))
            selected_question_ids = [question.id for question in random.sample(questions, num_questions_to_display)]
            request.session['selected_question_ids'] = selected_question_ids

        random_questions = QuizQuestion.objects.filter(id__in=selected_question_ids)
        print('random_questions:', random_questions)

        context = {'questions': random_questions}
        return render(request, 'trainingquiz.html', context)
    
    except Exception as e:
        larger_text = '''
        <div style="display: flex; justify-content: center; align-items: flex-start; height: 100vh;">
            <h1 style="font-size: 24px;">There are no questions</h1>
        </div>
    '''
        return HttpResponse(larger_text)

# from django.http import JsonResponse

def reassessmentquiz(request):
    try:
        if request.method == 'POST':
            mail = request.session.get('mail')
            user = User.objects.get(email=mail)
            logging.info('Employee accessed reassessment page')

            selected_options = {}

            for question_id, selected_option in request.POST.items():
                if question_id.startswith('q'):
                    selected_options[int(question_id[1:])] = selected_option

            questions_ids = list(selected_options.keys())
            values_list = list(selected_options.values())
            
            quiz_questions = QuizQuestion.objects.filter(id__in=questions_ids)
            answer_list = [question.correct_answer for question in quiz_questions]
            # difficulty_data = [question.difficulty for question in quiz_questions]

            matched_count = 0
            mismatched_pairs = []

            for val1, val2 in zip(values_list, answer_list):
                numeric_val2 = ord(val2.lower()) - ord('a') + 1
                if val1 == str(numeric_val2):
                    matched_count += 1
                else:
                    mismatched_pairs.append((val1, val2))

            total_user_quiz_score = matched_count * quiz_questions[0].marks  # Assuming all questions have the same marks
            category_data = quiz_questions[0].Technology_id  # Assuming all questions have the same Technology_id
            
            current_time = timezone.now()

            add_feedback1 = FinalQuizAnswer(
                quiz_domain=category_data,
                score=total_user_quiz_score,
                created_at=current_time,
                user_id=user.id,
            )

            add_feedback1.save()

            logging.info('Result submitted successfully!')
            messages.success(request, 'Result submitted successfully!')

            if total_user_quiz_score >= 10:

                context = {'user_name': user, 'time': current_time, 'score': total_user_quiz_score,
                           'text1':'Congratulations! You have successfully passed the quiz.'}

                return render(request, 'reassessment_result.html', context)
            else:
                context = {'user_name': user, 'time': current_time, 'score': total_user_quiz_score,
                           'text2':'I regret to inform you that you did not successfully pass the quiz.You are welcome to retake the quiz to improve your results'}

                return render(request, 'reassessment_result.html', context)
    except Exception as e:
        larger_text = '''
        <div style="display: flex; justify-content: center; align-items: flex-start; height: 100vh;">
            <h1 style="font-size: 24px;">There are no questions</h1>
        </div>
    '''
        return HttpResponse('Your quiz data not stored something went wrong')