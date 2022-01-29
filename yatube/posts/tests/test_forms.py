from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        cls.form = PostForm()

    def test_PostForm_create(self):
        """Тестируем PostForm."""
        form_data = {
            'text': 'Тестовый текст',
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={'username': 'HasNoName'}))

    def test_PostForm_edit(self):
        """Тестируем PostForm."""
        form_data = {
            'text': 'Тестовый текст',
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': PostFormTest.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={'post_id': PostFormTest.post.pk}))

