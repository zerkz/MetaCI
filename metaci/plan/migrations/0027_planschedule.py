# Generated by Django 2.2 on 2019-05-15 02:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("repository", "0006_remove_repository_public"),
        ("plan", "0026_auto_20190209_0101"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlanSchedule",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "schedule",
                    models.CharField(
                        choices=[("daily", "Daily"), ("hourly", "Hourly")],
                        max_length=16,
                    ),
                ),
                (
                    "branch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="repository.Branch",
                    ),
                ),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="plan.Plan"
                    ),
                ),
            ],
            options={"verbose_name_plural": "Plan Schedules"},
        )
    ]
