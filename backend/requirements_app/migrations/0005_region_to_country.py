from django.db import migrations, models


def set_country_to_china(apps, schema_editor):
    RequirementRequest = apps.get_model('requirements_app', 'RequirementRequest')
    RequirementRequest.objects.all().update(country='China')


class Migration(migrations.Migration):

    dependencies = [
        ('requirements_app', '0004_requirementrequest_estimated_completion_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='requirementrequest',
            name='country',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.RunPython(set_country_to_china, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='requirementrequest',
            name='region',
        ),
    ]
