"""Background tasks that send the account emails via the RQ worker."""

from email.message import MIMEPart
from pathlib import Path

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from auth_app.utils import build_frontend_link

LOGO_PATH = Path(__file__).resolve().parent / 'assets' / 'videoflix_logo.png'
ACTIVATION_PAGE = 'pages/auth/activate.html'
PASSWORD_RESET_PAGE = 'pages/auth/confirm_password.html'


def get_logo_attachment():
    """Return the logo as an inline image that the HTML can reference."""
    logo = MIMEPart()
    logo.set_content(
        LOGO_PATH.read_bytes(),
        maintype='image',
        subtype='png',
        disposition='inline',
        cid='<videoflix_logo>',
    )
    return logo


def send_html_email(subject, template, context, recipient):
    """Render an email template as text and HTML and send it."""
    text_body = render_to_string(f'auth_app/emails/{template}.txt', context)
    html_body = render_to_string(f'auth_app/emails/{template}.html', context)
    message = EmailMultiAlternatives(
        subject=subject, body=text_body, to=[recipient]
    )
    message.attach_alternative(html_body, 'text/html')
    message.attach(get_logo_attachment())
    message.send()


def send_activation_email(user_id, token):
    """Send the email with the link that activates a new account."""
    user = User.objects.get(pk=user_id)
    link = build_frontend_link(ACTIVATION_PAGE, user, token)
    context = {'user_name': user.email, 'link': link}
    send_html_email('Confirm your email', 'activation', context, user.email)


def send_password_reset_email(user_id, token):
    """Send the email with the link that lets the user set a new password."""
    user = User.objects.get(pk=user_id)
    link = build_frontend_link(PASSWORD_RESET_PAGE, user, token)
    context = {'link': link}
    send_html_email(
        'Reset your Password', 'password_reset', context, user.email
    )
