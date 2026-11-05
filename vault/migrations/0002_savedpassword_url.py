from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='savedpassword',
            name='url',
            field=models.URLField(blank=True, max_length=300),
        ),
    ]
