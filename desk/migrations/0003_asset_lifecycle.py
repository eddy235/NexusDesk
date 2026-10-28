from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('desk','0002_ticketcomment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name='asset',
            name='status',
            field=models.CharField(max_length=16,default='available',choices=[
                ('available','Available'),('assigned','Assigned'),
                ('maintenance','Maintenance'),('retired','Retired')]),
        ),
        migrations.CreateModel(
            name='AssetEvent',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('event',models.CharField(max_length=240)),
                ('created_at',models.DateTimeField(auto_now_add=True)),
                ('actor',models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL,null=True,to=settings.AUTH_USER_MODEL)),
                ('asset',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='history',to='desk.asset')),
            ],
            options={'ordering':['-created_at','-id']},
        ),
    ]
