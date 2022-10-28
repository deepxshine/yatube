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
        """Провереряем конкретно ли работает метод __str__ у модели group"""
        self.assertEqual(PostModelTest.group.title, str(PostModelTest.group))

    def test_text_post_model(self):
        """Провереряем конкретно ли работает метод __str__ у модели post"""
        self.assertEqual(PostModelTest.post.text[:30], str(PostModelTest.post))
