from .signals import notify_new_comment_signal
from .models import TopicNotification
from django.utils import timezone


def notify_new_comment(comment):
    topic_notifications = TopicNotification.objects.filter(topic=comment.topic, is_active=True, is_read=True)\
        .exclude(user=comment.user)\

    for tn in topic_notifications:
        notify_new_comment_signal.send(sender=tn.__class__, topic_notification=tn)

    topic_notifications.update(comment=comment, is_read=False, action=TopicNotification.COMMENT, date=timezone.now())
