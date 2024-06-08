from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author_1 = User.objects.create(username='Лев Толстой')
        cls.author_2 = User.objects.create(username='Человек простой')
        notes_author_1 = [
            Note(
                title='Новость',
                text='Просто текст.',
                slug=f'slug_{index}',
                author=cls.author_1
            )
            for index in range(2)
        ]
        Note.objects.bulk_create(notes_author_1)

    def test_context_value_for_list(self):
        self.client.force_login(self.author_1)
        response = self.client.get(self.LIST_URL)
        self.assertIn(
            'object_list',
            response.context,
            '''
            Убедитесь, что в контекстную переменную объекта
            ListView, передается 'object_list'.
            '''
        )

    def test_content_for_list(self):
        self.client.force_login(self.author_1)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        all_authors = [notes.author for notes in object_list]
        for author in all_authors:
            self.assertEqual(
                self.author_1,
                author,
                '''
                Убедитесь, что в контекстную переменную объекта
                ListView, передается заметки только авторизированного
                пользователя.
                '''
            )


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            slug='slug_1',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_context_value_for_detail(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn(
            'note',
            response.context,
            '''
            Убедитесь, что в контекстную переменную объекта
            DetailView, передается передается 'note'.
            '''
        )

    def test_content_for_detail(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        note = response.context['note']
        self.assertEqual(
            self.note,
            note,
            '''
            Убедитесь, что в контекстную переменную объекта
            DetailView, передается передается 'note'.
            '''
        )


class TestAddOrEditPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            slug='slug',
            author=cls.author
        )

    def test_edit_has_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(
                user=self.client.force_login(self.author),
                name=name
            ):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
