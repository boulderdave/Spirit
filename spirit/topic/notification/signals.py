# -*- coding: utf-8 -*-
import django.dispatch
from .models import TopicNotification
from django.dispatch import receiver

notify_new_comment_signal = django.dispatch.Signal(providing_args=["topic_notification"])


@receiver(notify_new_comment_signal, sender=TopicNotification)
def notify_new_comment(sender, topic_notification, *args, **kwargs):
    # send_notification_email would go here...
    # This signal could be disconnected, and your own, in your own project, connected.
    pass
