from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0013_application_demand_note_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="proceed_to_stage2",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="application",
            name="proceed_datetime",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="application",
            name="stop_status",
            field=models.CharField(blank=True, choices=[("closed", "Closed"), ("abandoned", "Abandoned"), ("by_client", "By Client")], max_length=20),
        ),
        migrations.AddField(
            model_name="application",
            name="journal_number",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="application",
            name="journal_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="application",
            name="journal_screenshot",
            field=models.ImageField(blank=True, null=True, upload_to="journals/%Y/%m/"),
        ),
    ]
