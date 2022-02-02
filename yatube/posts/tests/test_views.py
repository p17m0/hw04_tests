from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.paginator import Page
from yatube.settings import QUANTITY

from ..models import Post, Group


User = get_user_model()


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug=3
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=cls.group
        )

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:posts_group', kwargs={'slug': self.group.slug})):
                'posts/group_list.html',
            (reverse('posts:profile',
                     kwargs={'username': self.user.username})):
                'posts/profile.html',
            (reverse('posts:post_detail',
                     kwargs={'post_id': PagesTests.post.pk})):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            (reverse('posts:post_edit',
                     kwargs={'post_id': PagesTests.post.pk})):
                'posts/create_post.html',
        }
        # Проверяем, что при обращении
        # к name вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        # Проверяем, что типы полей
        # формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_edit_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': PagesTests.post.pk}))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        # Проверяем, что типы полей
        # формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context страницы /posts
    # в первом элементе списка object_list содержит ожидаемые значения
    def test_posts_group_show_correct_context(self):
        """Шаблон task_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:posts_group', kwargs={'slug': self.group.slug}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        objecta = response.context.get('group')
        page_obj = response.context.get('page_obj')
        title_0 = objecta.title
        description_0 = objecta.description
        slug_0 = objecta.slug
        self.assertEqual(title_0, self.group.title)
        self.assertEqual(description_0, self.group.description)
        self.assertEqual(slug_0, str(self.group.slug))
        self.assertIsInstance(page_obj, Page)
        self.assertEqual(len(page_obj), 1)

    # Проверяем, что словарь context страницы task/test-slug
    # содержит ожидаемые значения
    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PagesTests.post.pk})))
        self.assertEqual(response.context.get('post').text, self.post.text)

    def test_profile(self):
        """Шаблон profile проверка контекста."""
        response = (self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username})))
        page_obj = response.context.get('page_obj')
        self.assertIsInstance(page_obj, Page)
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(response.context.get('author').username, 'HasNoName')

    def test_index(self):
        """Проверка view index."""
        response = self.client.get(reverse('posts:index'))
        page_obj = response.context.get('page_obj')
        self.assertIsInstance(page_obj, Page)
        self.assertEqual(len(page_obj), 1)
        self.assertIsInstance(page_obj[0], Post)


class PaginationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PaginationTest, cls).setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug=3
        )
        for i in range(15):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'{i}',
                group=cls.group
            )
        cls.posts_count = Post.objects.count()
        cls.second_quantity = cls.posts_count - QUANTITY

    def test_index_pagina(self):
        """Проверка view index pagina."""
        response = self.client.get(reverse('posts:index'))
        page_obj = response.context.get('page_obj')
        self.assertEqual(len(page_obj), QUANTITY)

    def test_index_second_page_contains_five_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')), self.second_quantity)

    def test_profile(self):
        """Шаблон profile проверка контекста."""
        response = (self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username})))
        page_obj = response.context.get('page_obj')
        self.assertEqual(len(page_obj), QUANTITY)

    def test_profile_second_page_contains_five_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = (self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username}) + '?page=2'))
        self.assertEqual(len(response.context.get('page_obj')), self.second_quantity)

    def test_group_list_paginator(self):
        response = self.authorized_client.get(
            reverse('posts:posts_group', kwargs={'slug': self.group.slug}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        page_obj = response.context.get('page_obj')
        self.assertEqual(len(page_obj), QUANTITY)

    def test_group_list_paginator_second_page(self):
        response = self.authorized_client.get(
            reverse('posts:posts_group',
                    kwargs={'slug': self.group.slug}) + '?page=2')
        page_obj = response.context.get('page_obj')
        self.assertEqual(len(page_obj), self.second_quantity)
