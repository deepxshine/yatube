from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import Client, TestCase
from django import forms
from django.core.cache import cache

from ..models import Group, Post, User, Follow


class PagesDataTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description',
        )
        cls.group_another = Group.objects.create(
            title='title2',
            slug='slug2',
            description='description1',
        )
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
            content_type='image/gif',
        )

        cls.post = Post.objects.create(
            text="Текст поста",
            author=cls.author,
            group=cls.group,
            image=uploaded,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def assert_equal_post_check(self, response, obj='page_obj'):
        if obj == 'post':
            post_page = response.context.get(obj)
        else:
            post_page = response.context.get(obj)[0]

        self.assertEqual(post_page.text, self.post.text)
        self.assertEqual(post_page.author, self.post.author)
        self.assertEqual(post_page.group, self.post.group)
        self.assertEqual(post_page.image, self.post.image)

    def test_form(self):
        """Проверка првильности формы для страницы редактирования
        и создания поста"""
        patterns = [
            reverse('posts:create'),
            reverse('posts:edit', kwargs={'post_id': self.post.id}),
        ]
        for page in patterns:
            with self.subTest(page=page):
                response = self.author_client.get(page)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField
                )
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField
                )

    def test_context_index_html(self):
        """Проверка контекста главной страницы"""
        response = self.author_client.get(reverse('posts:index'))
        self.assert_equal_post_check(response)

    def test_context_group_list_html(self):
        """Проверка контекста страницы групп"""
        response = self.author_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assert_equal_post_check(response)
        self.assertEqual(response.context.get('group'),
                         self.group)

    def test_context_profile_html(self):
        """Проверка контекста страницы профиля"""
        response = self.author_client.get(
            reverse('posts:profile', kwargs={'username': self.author.username})
        )
        self.assert_equal_post_check(response)
        self.assertEqual(response.context['author'], self.author)

    def test_context_post_detail(self):
        """Проверка контекста страницы поста"""
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assert_equal_post_check(response, 'post')
        self.assertEqual(response.context.get('posts_count'),
                         Post.objects.count())

    def test_post_on_correct_place(self):
        """Проверка правильности отобрпжения поста"""
        self.post_more = Post.objects.create(
            text='Текст поста',
            author=self.author,
            group=self.group_another,
        )

        url = reverse('posts:group_list',
                      kwargs={'slug': self.group_another.slug})
        self.assertEqual(
            self.author_client.get(url).context['page_obj'][0].group,
            self.post_more.group)
        self.assertNotEqual(
            self.author_client.get(url).context['page_obj'][0].group,
            self.post.group)

    def test_cache(self):
        """Проверка работы кэша"""
        post = Post.objects.create(
            text='Пост под кеш',
            author=self.author)
        content_add = self.author_client.get(
            reverse('posts:index')).content
        post.delete()
        content_delete = self.author_client.get(
            reverse('posts:index')).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_cache_clear = self.author_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_add, content_cache_clear)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description'
        )
        cls.set_post = Post.objects.bulk_create(
            [Post(text=(f'Текст поста{i}'),
                  author=cls.author,
                  group=cls.group, )
             for i in range(13)])

    def setUp(self):
        self.client = Client()

    def test_paginator(self):
        quantity_posts_on_first_page = 10
        quantity_posts_on_second_page = 3
        patterns = [
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username': self.author.username}),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
        ]
        page = '?page=2'
        obj = 'page_obj'
        for url in patterns:
            with self.subTest(url=url):
                self.assertEqual(
                    len(self.client.get(url).context.get(obj)),
                    quantity_posts_on_first_page)
                self.assertEqual(
                    len(self.client.get(url + page).context.get(obj)),
                    quantity_posts_on_second_page)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            text='a' * 13,
            author=cls.author,
        )
        cls.user = User.objects.create_user(username='user')

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user_client = Client()
        self.user_client.force_login(self.user)

    def test_follow_post(self):
        """Проверка отображения поста избранного автора"""
        post = Post.objects.create(
            author=self.author,
            text="123asd")
        Follow.objects.create(
            user=self.user,
            author=self.author)
        response = self.user_client.get(
            reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_unfollow_post(self):
        """Проверка отображения поста у неизбранных авторов"""
        post = Post.objects.create(
            author=self.author,
            text="Text")
        response = self.user_client.get(
            reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)
# python manage.py test posts.tests.test_views
