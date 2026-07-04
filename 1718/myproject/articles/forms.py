from django import forms
from .models import Comment, Article, Question, Answer
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 
from django.core.exceptions import ValidationError
import re


from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class CyrillicUserCreationForm(forms.ModelForm):
    username = forms.CharField(
        label="Имя пользователя",
        min_length=3,
        max_length=20,
        help_text=None,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Имя пользователя',
            'required': 'required',
            'pattern': '^[a-zA-Z0-9_а-яА-ЯёЁ]{3,20}$',
            'title': 'От 3 до 20 символов. Разрешены только русские/английские буквы, цифры и _',
            # ДОБАВЛЕНО: Говорим браузеру, что это имя пользователя
            'autocomplete': 'username', 
        })
    )
    email = forms.EmailField(
        label="Электронная почта (Email)",
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'example@domain.com',
            'required': 'required',
            # ДОБАВЛЕНО: Подсказка для автозаполнения почты
            'autocomplete': 'email', 
        }),
        error_messages={
            'invalid': 'Пожалуйста, введите корректный адрес электронной почты.',
            'required': 'Поле Email обязательно для заполнения.'
        }
    )
    password1 = forms.CharField(
        label="Пароль",
        min_length=8, 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите пароль',
            'required': 'required',
            # ДОБАВЛЕНО: Говорим браузеру, что это генерация НОВОГО пароля
            'autocomplete': 'new-password', 
        }),
        error_messages={'min_length': 'Пароль должен содержать не менее 8 символов.'} 
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Повторите пароль',
            'required': 'required',
            # ДОБАВЛЕНО: Подсказка для повтора нового пароля
            'autocomplete': 'new-password', 
        })
    )


    class Meta:
        model = User
        fields = ("username",)

    # Валидация: латиница + кириллица
    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        
        # РЕГУЛЯРНОЕ ВЫРАЖЕНИЕ: разрешает латиницу (a-z), кириллицу (а-я), цифры (0-9) и "_"
        if not re.match(r'^[a-zA-Z0-9_а-яА-ЯёЁ]+$', username):
            raise ValidationError(
                'Имя пользователя содержит недопустимые символы. Разрешены только русские и латинские буквы, цифры и знак подчеркивания.'
            )
            
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким именем уже зарегистрирован.')
            
        return username
    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        # Проверяем, нет ли уже в системе инженера с такой же почтой
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким Email уже зарегистрирован в системе АСУТП.')
        return email
    # Валидация совпадения паролей
        # Валидация совпадения паролей и их сложности на бэкенде
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1:
            # Проверяем длину
            if len(password1) < 8:
                self.add_error('password1', "Пароль должен содержать не менее 8 символов.")
            
            # Проверяем регулярным выражением наличие цифры (\d) и заглавной буквы ([A-ZА-ЯёЁ])
            if not re.search(r'\d', password1) or not re.search(r'[A-ZА-ЯёЁ]', password1):
                self.add_error('password1', "Пароль должен содержать хотя бы одну цифру и одну заглавную букву.")

        # Проверяем совпадение
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Пароли не совпадают.")
            
        return cleaned_data


    # Сохранение пользователя с хэшированием пароля
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class':'form-control',
                'rows': 4, 
                'placeholder': 'Оставьте ваш комментарий....' # Исправлена опечатка в placeholder
            })
        }

# Форма для статей с полем для фото
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'image', 'tags'] 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок статьи'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Текст статьи...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}), 
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content'] 

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Введите ваш ответ...'}), # Добавлен Bootstrap класс form-control для красоты
        }
