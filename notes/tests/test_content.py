from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):

    LIST_URL = reverse('notes:list')

    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Другой пользователь')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.list_url = reverse('notes:list')

    def test_for_author_and_not_author_list(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок,
        чужие заметки не попадают в список заметок.
        """
        params = (
            (self.author_client, True),
            (self.not_author_client, False)
        )
        for user, note_in_list in params:
            with self.subTest(name=user):
                response = user.get(self.list_url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_add_or_edit_has_form(self):
        """
        На страницы создания и редактирования заметки передаются формы.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
