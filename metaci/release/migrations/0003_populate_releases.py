# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-15 22:48
from __future__ import unicode_literals

import logging
import re

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations
from django.utils.dateparse import parse_date

from metaci.release.utils import update_release_from_github

logger = logging.getLogger(__name__)


def populate_releases(apps, schema_editor):
    Build = apps.get_model("build.Build")
    Release = apps.get_model("release.Release")

    repos = {}
    for build in Build.objects.filter(plan__role="release_test"):
        if build.branch.repo.id not in repos:
            repos[build.branch.repo.id] = {"repo": build.branch.repo, "tags": set()}
        repos[build.branch.repo.id]["tags"].add(build.branch.name.replace("tag: ", ""))

    for info in repos.values():
        repo_api = info["repo"].github_api
        for tag in info["tags"]:
            existing = Release.objects.filter(repo=info["repo"], git_tag=tag)
            if existing.exists():
                continue

            release = Release(repo=info["repo"], status="published", git_tag=tag)
            update_release_from_github(release, repo_api)
            release.save()


def populate_build_release(apps, schema_editor):
    Build = apps.get_model("build.Build")
    Release = apps.get_model("release.Release")

    for build in Build.objects.filter(plan__role__in=["release", "release_test"]):
        try:
            rel = Release.objects.get(
                repo=build.repo, git_tag=build.branch.name.replace("tag: ", "")
            )
        except ObjectDoesNotExist:
            logger.error("Couldn't find Release for build #{}".format(build.id))
            continue
        build.release = rel
        if build.plan.role == "release":
            build.release_relationship_type = "manual"
        else:
            build.release_relationship_type = "test"
        build.save()


class Migration(migrations.Migration):

    dependencies = [
        ("repository", "0005_repository_release_tag_regex"),
        ("release", "0002_auto_20180815_2248"),
    ]

    operations = [
        migrations.RunPython(populate_releases),
        migrations.RunPython(populate_build_release),
    ]
