from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text',)
        labels = {
            'text': ('Текст'),
            'group': ('Группа'),
        }
        help_texts = {
            'text': ('Внесите текст какой-нибудь текст:'),
            'group': ('Выберите группу:'),
        }
