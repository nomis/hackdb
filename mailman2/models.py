# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models


class MailingList(models.Model):
    NONE = 0
    CONFIRM = 1
    REQUIRE_APPROVAL = 2
    CONFIRM_AND_APPROVE = 3
    SUBSCRIBE_POLICY_CHOICES = [
        (NONE, "None"),
        (CONFIRM, "Confirm"),
        (REQUIRE_APPROVAL, "Require approval"),
        (CONFIRM_AND_APPROVE, "Confirm and approve"),
    ]

    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True)
    info = models.TextField(blank=True)
    advertised = models.BooleanField()
    subscribe_policy = models.SmallIntegerField(choices=SUBSCRIBE_POLICY_CHOICES)
    archive_private = models.BooleanField()
    subscribe_auto_approval = models.TextField(blank=True)
    auto_unsubscribe = models.BooleanField(
        default=False,
        help_text="Should non-group members be automatically unsubscribed?",
    )

    def __str__(self):
        return self.name

    def check_subscribe_auto_approval(self, address):
        for pattern in self.subscribe_auto_approval.split("\n"):
            if pattern.startswith("^"):
                if re.match(pattern, address):
                    return True
            elif pattern.lower() == address.lower():
                return True
        return False

    class Meta:
        permissions = [("audit_list", "Can audit the subscribers of a mailing list")]


class GroupPolicy(models.Model):
    ALLOW = 0
    RECOMMEND = 1
    PROMPT = 2
    FORCE = 3
    POLICY_CHOICES = [
        (ALLOW, "Allow"),
        (RECOMMEND, "Recommend"),
        (PROMPT, "Prompt"),
        (FORCE, "Force"),
    ]
    mailing_list = models.ForeignKey(
        MailingList, on_delete=models.CASCADE, related_name="group_policies"
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="mailinglist_policies"
    )
    policy = models.SmallIntegerField(choices=POLICY_CHOICES, default=ALLOW)
    prompt = models.TextField(blank=True)

    def __str__(self):
        return f"{self.mailing_list}:{self.group}:{self.get_policy_display()}"

    def clean(self):
        if self.policy == self.PROMPT:
            if not self.prompt:
                raise ValidationError("Must supply a message for a prompt policy.")

    class Meta:
        verbose_name_plural = "Group policies"
        unique_together = ("mailing_list", "group")


class ChangeOfAddress(models.Model):
    created = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    old_email = models.EmailField()
    new_email = models.EmailField()

    class Meta:
        verbose_name_plural = "Changes of address"
