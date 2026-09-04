from django.db import models
from django.contrib.auth.models import User


class GeneratedContent(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    topic = models.CharField(
        max_length=200
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.topic



class FollowUpConversation(models.Model):

    generated_content = models.ForeignKey(
        GeneratedContent,
        on_delete=models.CASCADE,
        related_name="followups"
    )

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.question





    from django.contrib.auth.models import User
from django.db import models


class VoiceConversation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="voice_conversations"
    )

    title = models.CharField(
        max_length=255,
        blank=True,
        default="New Conversation"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class VoiceMessage(models.Model):

    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
    )

    conversation = models.ForeignKey(
        VoiceConversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    text = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.role}: {self.text[:50]}"
