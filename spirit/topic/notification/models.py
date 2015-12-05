# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError, transaction

from .managers import TopicNotificationQuerySet


class TopicNotification(models.Model):
    UNDEFINED, MENTION, COMMENT = range(3)

    ACTION_CHOICES = (
        (UNDEFINED, _("Undefined")),
        (MENTION, _("Mention")),
        (COMMENT, _("Comment")),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='st_topic_notifications')
    topic = models.ForeignKey('spirit_topic.Topic', related_name='topic_notifications')
    comment = models.ForeignKey('spirit_comment.Comment', related_name='topic_notifications')

    date = models.DateTimeField(default=timezone.now)
    action = models.IntegerField(choices=ACTION_CHOICES, default=UNDEFINED)
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = TopicNotificationQuerySet.as_manager()

    class Meta:
        unique_together = ('user', 'topic')
        ordering = ['-date', '-pk']
        verbose_name = _("topic notification")
        verbose_name_plural = _("topics notification")

    def get_absolute_url(self):
        return self.comment.get_absolute_url()

    @property
    def text_action(self):
        return self.ACTION_CHOICES[self.action][1]

    @property
    def is_mention(self):
        return self.action == self.MENTION

    @property
    def is_comment(self):
        return self.action == self.COMMENT

    @classmethod
    def mark_as_read(cls, user, topic):
        if not user.is_authenticated():
            return

        cls.objects\
            .filter(user=user, topic=topic)\
            .update(is_read=True)

    @classmethod
    def create_maybe(cls, user, comment, is_read=True, action=None):
        if not action:
            action = cls.COMMENT
        # Create a dummy notification
        return cls.objects.get_or_create(
            user=user,
            topic=comment.topic,
            defaults={
                'comment': comment,
                'action': action,
                'is_read': is_read,
                'is_active': True
            }
        )

    @classmethod
    def notify_new_mentions(cls, comment, mentions):
        if not mentions:
            return

        # TODO: refactor
        for username, user in mentions.items():
            try:
                with transaction.atomic():
                    cls.objects.create(
                        user=user,
                        topic=comment.topic,
                        comment=comment,
                        action=cls.MENTION,
                        is_active=True
                    )
            except IntegrityError:
                pass

        cls.objects\
            .filter(user__in=mentions.values(), topic=comment.topic, is_read=True)\
            .update(comment=comment, is_read=False, action=cls.MENTION, date=timezone.now())

    @classmethod
    def bulk_create(cls, users, comment):
        return cls.objects.bulk_create([
            cls(user=user,
                topic=comment.topic,
                comment=comment,
                action=cls.COMMENT,
                is_active=True)
            for user in users
        ])
