# SPDX-FileCopyrightText: 2022 Tim Hawes <me@timhawes.com>
#
# SPDX-License-Identifier: MIT

from django.apps import AppConfig


class LdapsyncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ldapsync"

    def ready(self):
        from . import receivers
