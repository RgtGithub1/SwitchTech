from django import template
from home.models import User



register = template.Library()

@register.filter(name='fetch_user')
def fetch_user(user_mail):
    user_name = User.objects.filter(email=user_mail)
    user_name = [user.username for user in user_name]
    return user_name[0]
