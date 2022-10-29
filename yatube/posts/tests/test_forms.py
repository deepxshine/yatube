from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User, Comment


class PostTestsForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='descr'
        )
        cls.group_another = Group.objects.create(
            title='title',
            slug='slug2',
            description='descr'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    def setUp(self):
        self.user = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def check_equal(self, post, form_data):
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        if 'image' in form_data.items():
            self.assertEqual(post.image, form_data['image'])

    def test_post_create_by_login_user(self):
        """Проверка создания поста"""
        count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': self.group.id,
            'image': self.uploaded,
        }
        url = reverse('posts:create')
        response = self.author_client.post(url, data=form_data, follow=True)
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.author.username}))
        self.assertEqual(Post.objects.count(), count + 1)
        post = Post.objects.first()
        self.check_equal(post, form_data)

    def test_post_edit(self):
        """Проверка редактирования поста"""
        post = Post.objects.create(
            text='Текст поста который создал автор и он является классным...',
            author=self.author,
            group=self.group,
            image=''
        )
        form_data = {
            'text': 'Текст поста 2.0',
            'group': self.group_another.id,
        }
        url = reverse('posts:edit', kwargs={'post_id': post.id})
        response = self.author_client.post(url, data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.first()
        self.check_equal(post, form_data)
        old_group_response = self.author_client.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        self.assertEqual(
            old_group_response.context['page_obj'].paginator.count, 0)
        new_group_response = self.author_client.get(
            reverse('posts:group_list', args=(self.group_another.slug,))
        )
        self.assertNotEqual(
            new_group_response.context['page_obj'].paginator.count, 0)

    def test_post_guest_user(self):
        """Проверка создания поста неавторизированнм пользователем"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.user.post(reverse('posts:create'),
                                  data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), post_count)

    def check_equal_to_comments(self, redirect, client, post):
        """Вспомогательная функция для работы тестов"""

        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария'
        }
        url = reverse('posts:add_comment', kwargs={'post_id': post.id})
        if client == 'user':
            com_sum = 0
            response = self.user.post(url, data=form_data, follow=True)
        else:
            com_sum = 1
            response = self.author_client.post(url, data=form_data,
                                               follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, redirect)
        self.assertEqual(Comment.objects.count(),
                         comments_count + com_sum)

    def test_comments_to_auth_user(self):
        """Проверка создания комментария авторизированным пользователем"""
        post = Post.objects.create(
            text='Текст',
            group=self.group,
            author=self.author
        )
        redirect = reverse('posts:post_detail', kwargs={'post_id': post.id})
        self.check_equal_to_comments(redirect, 'author', post)

    def test_comment_to_not_auth_user(self):
        """Проверка создания комментария не авторизированным пользователем"""
        post = Post.objects.create(
            text='Текст',
            group=self.group,
            author=self.author
        )
        redirect = reverse('users:login') + '?next=' + reverse(
            'posts:add_comment', kwargs={'post_id': post.id})
        self.check_equal_to_comments(redirect, 'user', post)
