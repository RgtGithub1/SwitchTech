from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .models import MeetingTraining
from django.core import serializers
import logging


#POST REQUEST
@csrf_exempt
def add_meeting(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            meeting_type = data.get("meeting_type")
            extracted_data = {}  # Initialize an empty dictionary to hold extracted data
            model_class = None  # Initialize model_class with None

            if meeting_type == "custom":
                fields_to_extract = ['title', 'date', 'time', 'location', 'link']
                extracted_data = {field: data.get(field) for field in fields_to_extract}
                model_class = MeetingTraining

            elif meeting_type == "recurring":
                fields_to_extract = ['training_name', 'select_training', 'year', 'trainer_name', 'date', 'time',
                                     'location', 'link']
                extracted_data = {field: data.get(field) for field in fields_to_extract}
                model_class = MeetingTraining

            if model_class is not None:
                # Create and save the meeting instance
                meeting = model_class(**extracted_data, meeting_type=meeting_type)
                meeting.save()

                response_data = {
                    "message": "True.",
                    "meeting_details": extracted_data,
                }
                logging.info(f"{meeting_type} meeting scheduled successfully!")
                return JsonResponse(response_data, status=201)
            else:
                return JsonResponse({"message": "Invalid meeting type."}, status=400)
        except json.JSONDecodeError:
            logging.warning("Invalid JSON data")
            return JsonResponse({"message": "Invalid JSON data."}, status=400)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"message": "Invalid request method."}, status=405)


#GET REQUEST
def meeting_list(request):
    try:
        if request.method == 'GET':
            meetings = MeetingTraining.objects.all()
            if not meetings:
                logging.info("No meetings are avaliable")
                return JsonResponse({"message": "No meetings available."})
            meeting_data = serializers.serialize('json', meetings)

            parsed_data = []
            for entry in serializers.deserialize('json', meeting_data):
                meeting = entry.object
                meeting_dict = {
                    "meeting_type": meeting.meeting_type,
                    "title": meeting.title,
                    "training_name": meeting.training_name,
                    "select_training": meeting.select_training,
                    "year": meeting.year,
                    "trainer_name": meeting.trainer_name,
                    "date": str(meeting.date),
                    "time": str(meeting.time),
                    "location": meeting.location,
                    "link": meeting.link,
                }
                parsed_data.append(meeting_dict)

            return JsonResponse({"meetings": parsed_data})

        return JsonResponse({"message": "Invalid request method."}, status=405)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


#PUT REQUEST
@csrf_exempt
def edit_meeting(request, pk):
    if request.method == 'PUT':
        try:
            meeting = MeetingTraining.objects.get(pk=pk)
        except MeetingTraining.DoesNotExist:
            logging.info("Meeting not found.")
            return JsonResponse({"message": "Meeting not found."}, status=404)

        data = json.loads(request.body)
        # Update the meeting fields based on the data in the request
        meeting.meeting_type = data.get('meeting_type', meeting.meeting_type)
        meeting.title = data.get("title", meeting.title)
        meeting.training_name = data.get("training_name", meeting.training_name)
        meeting.select_training = data.get("select_training", meeting.select_training)
        meeting.year = data.get("year", meeting.year)
        meeting.trainer_name = data.get("trainer_name", meeting.trainer_name)
        meeting.date = data.get("date", meeting.date)
        meeting.time = data.get("time", meeting.time)
        meeting.location = data.get("location", meeting.location)
        meeting.link = data.get("link", meeting.link)
        meeting.save()

        logging.info("Meeting updated successfully!")
        return JsonResponse({"message": "Meeting updated successfully."})

    return JsonResponse({"message": "Invalid request method."}, status=405)


#DELETE REQUEST
@csrf_exempt
def delete_meeting(request, pk):
    if request.method == 'DELETE':
        try:
            meeting = MeetingTraining.objects.get(pk=pk)
            meeting.delete()
            logging.info("Meeting deleted successfully.")
            return JsonResponse({"message": "Meeting deleted successfully."})
        except MeetingTraining.DoesNotExist:
            logging.info("Meeting not found.")
            return JsonResponse({"message": "Meeting not found."}, status=404)

    return JsonResponse({"message": "Invalid request method."}, status=405)