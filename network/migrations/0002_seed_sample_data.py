from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_sample_data(apps, schema_editor):
    User = apps.get_model('network', 'User')
    Post = apps.get_model('network', 'Post')
    Comment = apps.get_model('network', 'Comment')

    sample_users = [
        {
            'username': 'skywalker',
            'email': 'skywalker@example.com',
            'password': 'Password123!',
            'bio': 'Solar-powered dreamer building new stories every day.',
        },
        {
            'username': 'daydreamer',
            'email': 'daydreamer@example.com',
            'password': 'Password123!',
            'bio': 'Coffee, code, and endless curiosity.',
        },
        {
            'username': 'foodie',
            'email': 'foodie@example.com',
            'password': 'Password123!',
            'bio': 'Exploring the city one bite at a time.',
        },
        {
            'username': 'codequeen',
            'email': 'codequeen@example.com',
            'password': 'Password123!',
            'bio': 'Building beautiful experiences with clean code.',
        },
        {
            'username': 'urbanexplorer',
            'email': 'urbanexplorer@example.com',
            'password': 'Password123!',
            'bio': 'Finding hidden gems and sharing them with friends.',
        },
    ]

    users = {}
    for sample in sample_users:
        user, created = User.objects.get_or_create(
            username=sample['username'],
            defaults={
                'email': sample['email'],
                'bio': sample['bio'],
                'is_active': True,
            }
        )
        if created:
            User.objects.filter(pk=user.pk).update(password=make_password(sample['password']))
            user = User.objects.get(pk=user.pk)
        users[sample['username']] = user

    if not Post.objects.exists():
        post1 = Post.objects.create(
            author=users['skywalker'],
            content='Good morning, world! The sunrise over the city was incredible today. 🌅',
        )
        post2 = Post.objects.create(
            author=users['daydreamer'],
            content='Just finished a new app idea — can’t wait to see what everyone thinks. 💡',
        )
        post3 = Post.objects.create(
            author=users['foodie'],
            content='Brunch at the hidden rooftop café was a total vibe. Highly recommend the blueberry pancakes!',
        )

        Comment.objects.create(post=post1, author=users['daydreamer'], content='That view looks amazing! I wish I was there. ☀️')
        Comment.objects.create(post=post2, author=users['codequeen'], content='Love that energy — ship it! 🚀')
        Comment.objects.create(post=post3, author=users['urbanexplorer'], content='Need the name of that cafe. Sounds delicious 😋')

    users['skywalker'].following.add(users['daydreamer'], users['foodie'])
    users['daydreamer'].following.add(users['codequeen'], users['urbanexplorer'])
    users['foodie'].following.add(users['urbanexplorer'], users['skywalker'])


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_sample_data),
    ]
