from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, Comment, Follow
from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тест групп',
            slug='test-slug',
            description='Тест описания'
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=User.objects.create_user(username='author_user'),
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='author_user2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        cache.clear()
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_posts', kwargs={'slug': 'test-slug'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': PostsViewsTests.author.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тест групп',
            slug='test-slug',
            description='Тест описания'
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=User.objects.create_user(username='author_user'),
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_context_index(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        text_0 = first_object.text
        author_0 = first_object.author.username
        self.assertEqual(text_0, 'Текст')
        self.assertEqual(author_0, 'author_user')

    def check_post_data(self, post):
        self.post = post
        self.assertEqual(self.post.text, PostsPagesTests.post.text)
        self.assertEqual(
            self.post.author.username, PostsPagesTests.post.author.username
        )

    def test_context_group(self):
        """Шаблон посты сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'test-slug'})
        )
        first_object = response.context['page_obj'][0]
        first_object2 = response.context['group']
        title_0 = first_object2.title
        self.assertEqual(title_0, 'Тест групп')
        self.check_post_data(first_object)

    def test_context_profile(self):
        """Шаблон профайл сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostsPagesTests.author.username})
        )
        author_context = response.context['author']
        name = author_context.username
        self.assertEqual(name, 'noname')

    def test_context_detail(self):
        """Шаблон детализации сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': '1'})
        )
        post_object = response.context['posts']
        num_object = post_object.pk
        self.assertEqual(num_object, 1)

    def test_context_create_edit(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create'), kwargs={'post_id': '1'}
        )
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_context_create(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тест групп',
            slug='test-slug',
            description='Тест описания'
        )
        for cases in range(1, 15):
            cls.post = Post.objects.create(
                text=f'Тест групп {cases}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_group_ten_records(self):
        response = self.client.get(reverse(
            ('posts:group_posts'), kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_profile_ten_records(self):
        response = self.client.get(reverse(
            ('posts:profile'),
            kwargs={'username': PaginatorViewsTest.user.username})
        )
        self.assertEqual(len(response.context['page_obj']), 5)


class SuccessViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тест групп',
            slug='test-slug',
            description='Тест описания',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=User.objects.create_user(username='author_user'),
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_success(self):
        response_1 = self.client.get(reverse('posts:index'))
        page_object = response_1.context['page_obj'][0]
        title_object = page_object.group.title

        response2 = self.client.get(reverse(
            ('posts:group_posts'), kwargs={'slug': 'test-slug'})
        )
        group_object = response2.context['group']
        title_object_2 = group_object.title
        self.assertEqual(title_object, title_object_2)


class ViewsTestImages(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тест',
            slug='test-slug'
        )
        cls.author = User.objects.create_user('DonDon')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Текст пост',
            author=cls.author,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def setUp(self):
        self.user = User.objects.create_user(username='DonPedro')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author = ViewsTestImages.author
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

        self.post = ViewsTestImages.post

        self.group = ViewsTestImages.group

    def check_post_data(self, post):
        self.post = post
        self.assertEqual(self.post.text, ViewsTestImages.post.text)
        self.assertEqual(
            self.post.author.username, ViewsTestImages.post.author.username
        )
        self.assertEqual(
            self.post.image, ViewsTestImages.post.image
        )

    def test_index_correct_context_usage(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.check_post_data(first_object)

    def test_group_page_correct_context_usage(self):
        """Шаблон group.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(
            response.context['group'].title, self.group.title
        )
        self.assertEqual(response.context['group'].slug, self.group.slug)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.image, self.post.image)

    def test_profile_correct_context_usage(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': self.author.username})
        )
        first_object = response.context['page_obj'][0]
        self.check_post_data(first_object)

    def test_1_page_correct_context(self):
        """Шаблон post.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context['posts']
        self.check_post_data(first_object)


class TestCommentsAdded(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = User.objects.create_user('Mask')
        cls.user_hater = User.objects.create_user('Rogozin')

        cls.post = Post.objects.create(
            text='пост',
            author=cls.user_author,
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_hater,
            text='текст',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_hater)
        self.authorized_client.force_login(self.user_author)
        self.comment = TestCommentsAdded.post
        self.post = TestCommentsAdded.post

    def test_comment_added_to_post(self):
        """Комменты мутятся, хейтеры рады"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={
                    'post_id': self.post.id
                    }))
        first_object = response.context['posts'].comments

        self.assertEqual(first_object, self.post.comments)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_author = User.objects.create_user('Mask')
        cls.user_hater = User.objects.create_user('Rogozin')

        cls.post = Post.objects.create(
            text='пост',
            author=cls.user_author,
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_hater,
            text='текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_hater)
        self.authorized_client.force_login(self.user_author)
        self.comment = CacheTest.post
        self.post = CacheTest.post

    def test_cache(self):
        """Кэш кэшируется"""
        response = self.guest_client.get(reverse('posts:index'))
        posts_all = response.context['page_obj']
        self.assertIn(self.post, posts_all)
        cache.clear()
        response2 = self.guest_client.get(reverse('posts:index'))
        posts_all2 = response2.context['page_obj']
        self.assertNotEquals(posts_all2, posts_all)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Pedro')
        cls.group = Group.objects.create(
            title='Текст',
            description='описание',
            slug='slug')
        cls.post = Post.objects.create(
            text='Текст',
            pub_date=Post.pub_date,
            author=cls.user,
            group=cls.group)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = FollowTest.post

    def test_follow(self):
        """Тест подписки."""
        user = User.objects.create_user(username='Hater')
        counter_0 = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', args={user, })
        )
        counter = Follow.objects.count()
        self.assertEqual(counter_0 + 1, counter)
        follower = Follow.objects.first()
        self.assertEqual(follower.author, user)
        self.assertEqual(follower.user, self.user)

    def test_unfollow(self):
        """Тест отписки."""
        Follow.objects.create(
            author=self.user, user=self.user
        )
        counter_0 = Follow.objects.count()

        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=(self.user,))
        )
        counter_1 = Follow.objects.count()
        self.assertEqual(counter_0, counter_1 + 1)
