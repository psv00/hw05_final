from posts.forms import PostForm
from posts.models import User, Post, Group, Comment
from django.test import Client, TestCase
from django.urls import reverse


class SuccessFormsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тест групп',
            slug='test-slug',
            description='Тест описания',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=User.objects.create_user(username='author_user'),

        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='pedro')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Task."""
        tasks_count = Post.objects.count()
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response_auth = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response_guest = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_guest, '/auth/login/?next=/create/')
        self.assertRedirects(response_auth, reverse(
            ('posts:profile'), kwargs={'username': 'pedro'})
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)


class SuccessFormsTestEd(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тест групп',
            slug='test-slug',
            description='Тест описания',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=User.objects.create_user(username='author_user'),
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='pedro')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def edit_edit(self):
        """Изменяется как надо"""
        form_data = {
            'text': 'Тестовый текст ред',
            'group': self.group.id,
        }
        response_guest_ed = self.guest_client.post(
            reverse('posts:post_edit'),
            data=form_data,
            follow=True
        )
        response_auth_ed = self.authorized_client.post(
            reverse('posts:post_edit'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_guest_ed, '/auth/login/?next=/create/')
        self.assertRedirects(response_auth_ed, reverse(
            ('posts:profile'), kwargs={'username': 'pedro'})
        )


class TestCommentCreate(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тест групп',
            slug='test-slug',
            description='Тест описания',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=User.objects.create_user(username='author_user'),

        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=User.objects.create_user(username='author_hater'),
            text='текст',
        )

        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='pedro')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment(self):
        """Тест формы комментариев"""
        counter_hater = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }

        response_guest = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response_guest, '/auth/login/?next=%2Fposts%2F1%2Fcomment'
        )

        self.assertEqual(Comment.objects.count(), counter_hater)
