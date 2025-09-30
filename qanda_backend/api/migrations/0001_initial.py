from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('display_name', models.CharField(blank=True, default='', max_length=120)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('title', models.CharField(max_length=255)),
                ('source', models.CharField(choices=[('manual', 'Manual Upload'), ('seed', 'Seed Data'), ('url', 'Web URL'), ('other', 'Other')], default='manual', max_length=32)),
                ('source_uri', models.TextField(blank=True, default='')),
                ('description', models.TextField(blank=True, default='')),
                ('tags', models.JSONField(blank=True, default=list)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentChunk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('chunk_index', models.PositiveIntegerField()),
                ('text', models.TextField()),
                ('token_count', models.PositiveIntegerField(default=0)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chunks', to='api.document')),
            ],
            options={
                'ordering': ['document_id', 'chunk_index'],
                'unique_together': {('document', 'chunk_index')},
            },
        ),
        migrations.CreateModel(
            name='Embedding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('vector', models.JSONField()),
                ('model', models.CharField(default='text-embedding-3-small', max_length=128)),
                ('dim', models.PositiveIntegerField(default=1536)),
                ('chunk', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='embedding', to='api.documentchunk')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('text', models.TextField()),
                ('retrieval_context', models.JSONField(blank=True, default=dict)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questions', to='api.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('answer_text', models.TextField()),
                ('model', models.CharField(default='gpt-4o-mini', max_length=128)),
                ('references', models.JSONField(blank=True, default=list)),
                ('meta', models.JSONField(blank=True, default=dict)),
                ('question', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='answer', to='api.question')),
            ],
        ),
    ]
