# Generated by Django 2.1 on 2018-08-31 02:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=32, unique=True)),
                ('email', models.CharField(max_length=32, unique=True)),
                ('org', models.CharField(max_length=100)),
                ('igem', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('interest', models.TextField(default='None')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Chassis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Circuit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=50)),
                ('Description', models.CharField(max_length=100)),
                ('Author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('Chassis', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='design.Chassis')),
            ],
        ),
        migrations.CreateModel(
            name='CircuitCombines',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Circuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Father', to='design.Circuit')),
            ],
        ),
        migrations.CreateModel(
            name='CircuitDevices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('X', models.IntegerField(default=0)),
                ('Y', models.IntegerField(default=0)),
                ('Circuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.Circuit')),
            ],
        ),
        migrations.CreateModel(
            name='CircuitLines',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Type', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='CircuitParts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('X', models.IntegerField()),
                ('Y', models.IntegerField()),
                ('Circuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.Circuit')),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteParts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_type', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('link', models.TextField(null=True)),
                ('picture', models.URLField(max_length=1000, null=True)),
                ('related', models.TextField(null=True)),
                ('yearRelation', models.CharField(max_length=1000)),
                ('trackRelation', models.CharField(max_length=1000)),
                ('medalRelation', models.CharField(max_length=1000)),
                ('weightedRelated', models.TextField(null=True)),
                ('suggestedProject', models.TextField(null=True)),
                ('suggestedPart', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Papers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('DOI', models.CharField(default='', max_length=180, unique=True)),
                ('Title', models.CharField(default='', max_length=200)),
                ('Journal', models.CharField(default='', max_length=200)),
                ('JIF', models.FloatField(default=0)),
                ('ArticleURL', models.URLField(max_length=500)),
                ('LogoURL', models.URLField(max_length=600, null=True)),
                ('Abstract', models.TextField(default='To be add')),
                ('Keywords', models.TextField(default='To be add')),
                ('Authors', models.TextField(default='To be add')),
                ('Copyright', models.TextField(default='To be add')),
                ('ReadCount', models.IntegerField(default=0)),
                ('Circuit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='design.Circuit')),
            ],
        ),
        migrations.CreateModel(
            name='Parts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Username', models.CharField(default='Unknown', max_length=32)),
                ('IsPublic', models.BooleanField(default=True)),
                ('Role', models.CharField(default='sequenceFeature', max_length=20)),
                ('Name', models.CharField(db_index=True, max_length=50, unique=True)),
                ('secondName', models.TextField(default='Unknow')),
                ('Description', models.TextField()),
                ('Length', models.IntegerField(default=0)),
                ('Part_rating', models.IntegerField(default=0)),
                ('Type', models.CharField(max_length=20)),
                ('Safety', models.IntegerField(default=-1)),
                ('Scores', models.FloatField(default=-1.0)),
                ('Release_status', models.CharField(default='To be add', max_length=100)),
                ('Twins', models.CharField(default='To be add', max_length=500)),
                ('Sample_status', models.CharField(default='To be add', max_length=50)),
                ('Part_results', models.CharField(default='To be add', max_length=16)),
                ('Use', models.CharField(default='To be add', max_length=50)),
                ('Group', models.CharField(default='To be add', max_length=100)),
                ('Author', models.CharField(default='To be add', max_length=256)),
                ('DATE', models.CharField(default='To be add', max_length=10)),
                ('Distribution', models.TextField(default='To be add')),
                ('Sequence', models.TextField()),
                ('Parameter', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='PartsInteract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('InteractType', models.CharField(default='normal', max_length=10)),
                ('Score', models.FloatField(default=-1.0)),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child_part', to='design.Parts')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_part', to='design.Parts')),
            ],
        ),
        migrations.CreateModel(
            name='Protocol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Title', models.CharField(max_length=30)),
                ('Description', models.TextField()),
                ('Circuit', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='design.Circuit')),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Title', models.CharField(max_length=30)),
                ('Body', models.TextField()),
                ('Order', models.IntegerField()),
                ('Father', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.Protocol')),
            ],
            options={
                'ordering': ['Order'],
            },
        ),
        migrations.CreateModel(
            name='SubParts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child_name', to='design.Parts')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_name', to='design.Parts')),
            ],
        ),
        migrations.CreateModel(
            name='TeamImg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=180, unique=True)),
                ('URL', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='TeamKeyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=100)),
                ('score', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Trelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserFavorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('circuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.Circuit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Works',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TeamID', models.IntegerField(unique=True)),
                ('Teamname', models.CharField(max_length=32)),
                ('Region', models.CharField(max_length=32)),
                ('Country', models.CharField(max_length=50)),
                ('Track', models.CharField(max_length=32)),
                ('Size', models.IntegerField()),
                ('Status', models.CharField(max_length=32)),
                ('Year', models.IntegerField()),
                ('Wiki', models.URLField(max_length=128)),
                ('Section', models.CharField(max_length=32)),
                ('Medal', models.CharField(max_length=128)),
                ('Award', models.CharField(max_length=512)),
                ('Use_parts', models.TextField()),
                ('Title', models.CharField(max_length=256)),
                ('Description', models.TextField(default='To be add')),
                ('SimpleDescription', models.TextField(default='To be add')),
                ('Keywords', models.CharField(default='', max_length=200)),
                ('Chassis', models.CharField(default='None', max_length=100)),
                ('IEF', models.FloatField(default=0.0)),
                ('ReadCount', models.IntegerField(default=0)),
                ('DefaultImg', models.URLField(default='static\\img\\Team_img\\none.jpg')),
                ('logo', models.URLField(default='static\\img\\Team_img\\none.jpg')),
                ('Circuit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='design.Circuit')),
                ('Img', models.ManyToManyField(to='design.TeamImg')),
            ],
        ),
        migrations.AddField(
            model_name='trelation',
            name='first',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='first_work', to='design.Works'),
        ),
        migrations.AddField(
            model_name='trelation',
            name='second',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='second_work', to='design.Works'),
        ),
        migrations.AddField(
            model_name='teamkeyword',
            name='Team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Teamwork', to='design.Works'),
        ),
        migrations.AddField(
            model_name='favoriteparts',
            name='part',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.Parts'),
        ),
        migrations.AddField(
            model_name='favoriteparts',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='circuitparts',
            name='Part',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='design.Parts'),
        ),
        migrations.AddField(
            model_name='circuitlines',
            name='End',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='End', to='design.CircuitParts'),
        ),
        migrations.AddField(
            model_name='circuitlines',
            name='Start',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Start', to='design.CircuitParts'),
        ),
        migrations.AddField(
            model_name='circuitdevices',
            name='Subparts',
            field=models.ManyToManyField(to='design.CircuitParts'),
        ),
        migrations.AddField(
            model_name='circuitcombines',
            name='Father',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Sons', to='design.CircuitParts'),
        ),
        migrations.AddField(
            model_name='circuitcombines',
            name='Sons',
            field=models.ManyToManyField(to='design.CircuitParts'),
        ),
    ]
