from .models import QuizQuestion, FinalQuizAnswer
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils import timezone
from django.contrib import messages
import logging
import random
from home.models import Video


def reassessment_questions(request):
    '''
        This method will render questions for second
        quiz based on difficulty level of video watched
    '''
    try:
        category = request.GET.get('category')
        video_id_datas = request.GET.get('video_id_data')
        difficulty_level = list(Video.objects.filter(
            video_id=video_id_datas).values('difficulty'))
        difficulty_level_id = [
            video['difficulty'] for video in difficulty_level]
        difficulty_level_data = difficulty_level_id[0]
        selected_question_ids = request.session.get('selected_question_ids')
        if selected_question_ids is None:
            num_questions_to_display = 10
            questions = list(QuizQuestion.objects.filter(
                Technology__category_name=category,
                difficulty=difficulty_level_data))
            selected_question_ids = [question.id for question in random.sample(
                questions,
                num_questions_to_display)]
            request.session['selected_question_ids'] = selected_question_ids
        random_questions = QuizQuestion.objects.filter(
            id__in=selected_question_ids)
        context = {'questions': random_questions}
        return render(request, 'trainingquiz.html', context)
    except Exception as e:
        logging.error(f"{e}")
        data = {
            'no_data': True
        }
        return render(request, 'trainingquiz.html', context=data)


def validate_reassessment(request):
    '''
    This method will validate answers and calculate score for second quiz
    '''
    try:
        if request.method == 'POST':
            mail = request.session.get('mail')
            user = User.objects.get(email=mail)
            selected_options = {}
            for question_id, selected_option in request.POST.items():
                if question_id.startswith('q'):
                    selected_options[int(question_id[1:])] = selected_option
            questions_ids = list(selected_options.keys())
            values_list = list(selected_options.values())
            quiz_questions = QuizQuestion.objects.filter(id__in=questions_ids)
            answer_list = [
                question.correct_answer for question in quiz_questions]
            matched_count = 0
            mismatched_pairs = []
            for selected_answers, answer_list_data in zip(values_list,
                                                          answer_list):
                numeric_val2 = ord(answer_list_data.lower()) - ord('a') + 1
                if selected_answers == str(numeric_val2):
                    matched_count += 1
                else:
                    mismatched_pairs.append((selected_answers,
                                             answer_list_data))
            total_user_quiz_score = matched_count * quiz_questions[0].marks
            category_data = quiz_questions[0].Technology_id
            current_time = timezone.now()
            save_quiz_answer = FinalQuizAnswer(
                quiz_domain=category_data,
                score=total_user_quiz_score,
                created_at=current_time,
                user_id=user.id,
            )

            save_quiz_answer.save()
            if 'selected_question_ids' in request.session:
                del request.session['selected_question_ids']

            logging.info('Reassessment result submitted successfully!')
            messages.success(request, 'Result submitted successfully!')

            if total_user_quiz_score > 70:

                context = {'user_name': user,
                           'time': current_time,
                           'score': total_user_quiz_score,
                           'text1': 'Congratulations! You have '
                                    'successfully passed the quiz.'}

                return render(request, 'reassessment_result.html', context)
            else:
                context = {'user_name': user,
                           'time': current_time,
                           'score': total_user_quiz_score,
                           'text2': 'I regret to inform you that '
                                    'you did not successfully pass the quiz.'
                                    'You are welcome to retake the quiz '
                                    'to improve your results'}
                return render(request, 'reassessment_result.html', context)
    except Exception as e:
        logging.error(f"{e}")
        data = {
            'no_data': True
        }
        return render(request, 'reassessment_result.html', context=data)
