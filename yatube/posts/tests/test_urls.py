from django.core.cache import cache
from django.test import TestCase, Client
from ..models import Group, Post, User
from http import HTTPStatus
from django.urls import reverse


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create(
            username='auth_user'
        )
        cls.author = User.objects.create(
            username='leo'
        )
        cls.group = Group.objects.create(
            title='Название группы',
            description='descr',
            slug='slug',
        )
        cls.post = Post.objects.create(
            text='Текст поста который создал автор и он является классным...',
            author=cls.author,
            group=cls.group,
            id=2
        )
        cls.patterns_for_all = [
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.author.username}/',
            f'/posts/{cls.post.id}/',
        ]

        cls.patterns_private = [
            '/create/',
            f'/posts/{cls.post.id}/edit/'
        ]

        cls.patterns_404 = [
            '/group_list/error',
            '/untexting_page/',
        ]

    def setUp(self):
        self.non_auth_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.auth_user)
        self.author_client = Client()
        self.author_client.force_login(self.author)
        cache.clear()

    def check_access(self, patterns, http_status, client):
        for url in patterns:
            with self.subTest(url=url):
                if client == 'non_auth':
                    response = self.non_auth_client.get(url)
                    self.assertEqual(response.status_code, http_status)
                if client == 'auth':
                    response = self.auth_client.get(url)
                    self.assertEqual(response.status_code, http_status)
                if client == 'author':
                    response = self.author_client.get(url)
                    self.assertEqual(response.status_code, http_status)

    def test_access_to_not_auth_user(self):
        """Проверка доступа к страницам неавторизованному пользователю"""

        self.check_access(self.patterns_for_all, HTTPStatus.OK, 'non_auth')
        self.check_access(self.patterns_private, HTTPStatus.FOUND,
                          'non_auth')
        self.check_access(self.patterns_404, HTTPStatus.NOT_FOUND, 'non_auth')

    def test_access_to_auth_user(self):
        """Проверка доступа к страницам авторизованному пользователю"""
        edit_url = f'/posts/{self.post.id}/edit/'
        create_url = '/create/'
        self.assertEqual(
            self.auth_client.get(edit_url).status_code,
            HTTPStatus.FOUND)
        self.assertEqual(
            self.auth_client.get(create_url).status_code,
            HTTPStatus.OK)

    def test_access_to_author_user(self):
        """Проверка доступа к страницам автору"""
        self.check_access(self.patterns_private, HTTPStatus.OK, 'author')

    def test_correct_templates(self):
        """Проверка правильности вызываемых шаблонов"""
        pattens = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.author}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        for url, template in pattens.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
