from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('desk', '0003_asset_lifecycle')]
    operations = [
        migrations.AddField(
            model_name='ticket',
            name='sla_escalated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='SLAPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.CharField(choices=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')], max_length=12, unique=True)),
                ('resolution_hours', models.PositiveSmallIntegerField()),
                ('open_hour', models.PositiveSmallIntegerField(default=9)),
                ('close_hour', models.PositiveSmallIntegerField(default=17)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
    ]
