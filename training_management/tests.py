from django.test import TestCase, Client
from .models import MeetingTraining
from django.urls import reverse
import json


class MeetingTrainingTestCase(TestCase):
    def setUp(self):
        MeetingTraining.objects.create(
            meeting_type='custom',
            title='Custom Meeting',
            training_name='Sample Training',
            select_training='Option 1',
            year='2023',
            trainer_name='John Doe',
            date='2023-08-25',
            time='12:00:00',
            location='Conference Room A',
            link='https://example.com'
        )

    def test_meeting_training_str(self):
        meeting = MeetingTraining.objects.get(title='Custom Meeting')
        self.assertEqual(str(meeting), 'Custom Meeting')

    def test_meeting_training_fields(self):
        meeting = MeetingTraining.objects.get(title='Custom Meeting')
        self.assertEqual(meeting.meeting_type, 'custom')
        self.assertEqual(meeting.training_name, 'Sample Training')
        self.assertEqual(meeting.select_training, 'Option 1')
        self.assertEqual(meeting.year, '2023')
        self.assertEqual(meeting.trainer_name, 'John Doe')
        self.assertEqual(str(meeting.date), '2023-08-25')
        self.assertEqual(str(meeting.time), '12:00:00')
        self.assertEqual(meeting.location, 'Conference Room A')
        self.assertEqual(meeting.link, 'https://example.com')

    def test_meeting_training_empty_fields(self):
        meeting = MeetingTraining.objects.create(
            meeting_type='recurring',
            title='Recurring Meeting',
            date='2023-08-25',
            time='13:00:00',
            location='Conference Room B'
        )
        self.assertEqual(meeting.training_name, None)
        self.assertEqual(meeting.select_training, None)
        self.assertEqual(meeting.year, None)
        self.assertEqual(meeting.trainer_name, None)
        self.assertEqual(meeting.link, None)


class AddMeetingTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_add_custom_meeting(self):
        data = {
            "meeting_type": "custom",
            "title": "Custom Meeting",
            "date": "2023-08-25",
            "time": "12:00:00",
            "location": "Conference Room A",
            "link": "https://example.com"
        }

        response = self.client.post(reverse('training_management:add_meeting'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(MeetingTraining.objects.count(), 1)

        meeting = MeetingTraining.objects.get(title='Custom Meeting')
        self.assertEqual(meeting.meeting_type, 'custom')
        self.assertEqual(str(meeting.date), '2023-08-25')
        self.assertEqual(str(meeting.time), '12:00:00')
        self.assertEqual(meeting.location, 'Conference Room A')
        self.assertEqual(meeting.link, 'https://example.com')

    def test_add_recurring_meeting(self):
        data = {
            "meeting_type": "recurring",
            "training_name": "Sample Training",
            "select_training": "Option 1",
            "year": "2023",
            "trainer_name": "Karthik",
            "date": "2023-08-25",
            "time": "13:00:00",
            "location": "Microsoft Teams",
            "link": "https://example.com"
        }

        response = self.client.post(reverse('training_management:add_meeting'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(MeetingTraining.objects.count(), 1)

        meeting = MeetingTraining.objects.get(training_name='Sample Training')
        self.assertEqual(meeting.meeting_type, 'recurring')
        self.assertEqual(meeting.training_name, 'Sample Training')
        self.assertEqual(meeting.select_training, 'Option 1')
        self.assertEqual(meeting.year, '2023')
        self.assertEqual(meeting.trainer_name, 'Karthik')
        self.assertEqual(str(meeting.date), '2023-08-25')
        self.assertEqual(str(meeting.time), '13:00:00')
        self.assertEqual(meeting.location, 'Microsoft Teams')
        self.assertEqual(meeting.link, 'https://example.com')


class MeetingListTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create sample meetings for testing
        MeetingTraining.objects.create(
            meeting_type='custom',
            title='Custom Meeting 1',
            date='2023-08-25',
            time='12:00:00',
            location='Conference Room A',
            link='https://example.com'
        )
        MeetingTraining.objects.create(
            meeting_type='recurring',
            title='Recurring Meeting 1',
            training_name='Sample Training 1',
            date='2023-08-26',
            time='13:00:00',
            location='Conference Room B',
            link='https://example.com'
        )

    def test_meeting_list(self):
        response = self.client.get(reverse('training_management:meeting_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('meetings')), 2)


