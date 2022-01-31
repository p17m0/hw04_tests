from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=3,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group)

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
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': 'HasNoName'}))
        first_post = Post.objects.last()
        posts_count = Post.objects.count()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(first_post.text, PostFormTest.post.text)
        self.assertEqual(first_post.group, PostFormTest.post.group)

    def test_PostForm_edit(self):
        """Тестируем PostForm."""
        self.post = Post.objects.create(
            author=PostFormTest.user,
            text='Тестовый текст',
            group=PostFormTest.group)
        form_data = {
            'text': 'Тестовый текст1',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.pk}))

    def test_PostForm_edit_guest(self):
        """Тестируем PostForm."""
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.guest_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        login = redirect_to_login(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk})).url
        self.assertRedirects(response, login)
        posts_count = Post.objects.count()
        self.assertEqual(Post.objects.count(), posts_count)

    def test_PostForm_create_guest(self):
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        login = redirect_to_login(reverse('posts:post_create')).url
        self.assertRedirects(response, login)
        posts_count = Post.objects.count()
        self.assertEqual(Post.objects.count(), posts_count)
