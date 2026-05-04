from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add ref_number field to Application model.
    Format: XX-DDMM-NNN  e.g. BX-2904-037
    Run: python manage.py migrate cases
    """

    dependencies = [
        ('cases', '0014_application_workflow_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='ref_number',
            field=models.CharField(
                max_length=20,
                unique=True,
                blank=True,
                verbose_name='Ref #',
                help_text='Auto-generated internal ID (e.g. BX-2904-037)',
                default='',
            ),
            preserve_default=False,
        ),
    ]
