from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.home,
        name="home"
    ),

    path(
        'generate/',
        views.generate_content,
        name="generate"
    ),

    path(
        'translate/',
        views.translate_content,
        name="translate"
    ),

    path(
        'followup/',
        views.followup_question,
        name="followup"
    ),

    path(
        'about/',
        views.about,
        name="about"
    ),

    path(
        'contact/',
        views.contact,
        name="contact"
    ),

    path(
        'download/pdf/<int:id>/',
        views.download_pdf,
        name="download_pdf"
    ),

    path(
        'download/ppt/<int:id>/',
        views.download_ppt,
        name="download_ppt"
    ),




    path(
    'voice-tutor/',
    views.voice_tutor_page,
    name="voice_tutor"
),

path(
    'voice-tutor/chat/',
    views.voice_tutor_chat,
    name="voice_tutor_chat"
),

    
    
]