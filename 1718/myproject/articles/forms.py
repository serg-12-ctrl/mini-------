from django import forms
from .models import Comment, Article
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 
from .models import Question
from .models import Answer


class CyrillicUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class':'form-control',
                'rows': 4, 
                'placeholder': 'Оставьте ваш комменатрий....'
            })
        }


# НОВАЯ форма для статей с полем для фото
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        
        fields = ['title', 'content', 'image', 'tags'] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок статьи'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Текст статьи...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}), # Поле для файла
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }



class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content'] # Поля 'forum' и 'author' мы заполним автоматически в View




class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Введите ваш ответ...'}),
        }
