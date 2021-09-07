from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group, Follow
from http import HTTPStatus


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)


class TaskURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.group = Group.objects.create(
            title='Тест групп',
            slug='slug',
            description='Тест описания'
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=User.objects.create_user(username='author_user'),
            group=cls.group
        )
        cls.follow = Follow.objects.create(
            user=User.objects.create_user(username='user'),
            author=User.objects.create_user(username='author')
        )
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='KukuKu')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_profile_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/profile/KukuKu/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_group_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/group/slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_posts_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_edit_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_create_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_null_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_comment_url_exists_at_desired_location(self):
        """Страница Коммент только для авториз / доступна любому."""
        response = self.guest_client.get('/posts/1/comment/')
        self.assertEqual(response.status_code, 404)

    def test_comment_url_follow(self):
        """Кнопка подписки сработала."""
        response = self.authorized_client.get('/profile/KukuKu/follow/')
        self.assertRedirects(
            response, '/profile/KukuKu/'
        )

    def test_comment_url_follow(self):
        """Кнопка подписки сработала."""
        response = self.authorized_client.get('/profile/author/unfollow/')
        self.assertRedirects(
            response, '/profile/author/'
        )
