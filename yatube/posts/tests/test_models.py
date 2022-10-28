from django.test import TestCase
from ..models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Group test',
            slug='testgroup',
            description='description123',
        )
        cls.post = Post.objects.create(
            text=('абвгд' * 150),
            group=PostModelTest.group,
            author=cls.user,
        )

    def test_title_group_model(self):
        """Проверка метода __str__ у модели group"""
        self.assertEqual(PostModelTest.group.title, str(PostModelTest.group))

    def test_text_post_model(self):
        """Провереряем конкретно ли работает метод __str__ у модели post"""
        self.assertEqual(PostModelTest.post.text[:30], str(PostModelTest.post))

    def test_verbose_name(self):
        """Проверка verbose_name у модели"""
        verbose_names = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        for field, verbose in verbose_names.items():
            with self.subTest(field=field):
                verbose_name = self.post._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name, verbose)

    def test_help_text(self):
        """Проверка работы help_text"""
        help_texts = {
            'text': 'Текст поста',
            'group': 'Группа поста',
        }
        for field, text in help_texts.items():
            with self.subTest(field=field):
                help_text = self.post._meta.get_field(field).help_text
                self.assertEqual(text, help_text)
