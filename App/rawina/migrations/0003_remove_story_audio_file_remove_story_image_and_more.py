# Generated by Django 5.2.3 on 2025-07-07 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rawina', '0002_remove_story_audio_url_remove_story_images_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='story',
            name='audio_file',
        ),
        migrations.RemoveField(
            model_name='story',
            name='image',
        ),
        migrations.AlterField(
            model_name='story',
            name='generated_text',
            field=models.TextField(help_text='Text generated by the model'),
        ),
        migrations.AlterField(
            model_name='story',
            name='prompt',
            field=models.TextField(help_text='Prompt used to generate the story'),
        ),
        migrations.AlterField(
            model_name='story',
            name='title',
            field=models.CharField(help_text='Story Title', max_length=100),
        ),
    ]
