from django.contrib.auth.models import Group,Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps


@receiver(post_migrate)
def create_editor_group(sender, **kwargs):
    if sender.label != 'movie_site':
        return
    editor_group, created = Group.objects.get_or_create(name='Editors')

    app_label = 'movie_site'

    permissions = Permission.objects.filter(content_type__app_label=app_label,
                                            codename__in=[
                                                'edit_media',
                                                'view_media',
                                            ])
    editor_group.permissions.add(*permissions)
    editor_group.save()
    print('Created editor group')


@receiver(post_migrate)
def create_moderators(sender, **kwargs):
    if sender.label != 'movie_site':
        return

    moderator_group, created = Group.objects.get_or_create(name='Moderators')

    app_label = 'movie_site'

    permissions = Permission.objects.filter(content_type__app_label=app_label,
                                            codename__in=[
                                                'view_user_media',
                                                'edit_user_media',
                                                'delete_user_media',
                                            ])
    moderator_group.permissions.add(*permissions)
    moderator_group.save()
    print('Created moderator group')
