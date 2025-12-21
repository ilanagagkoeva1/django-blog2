#Формы через Django упрощают создание форм, их валидацию (проверку)
from django import forms
#наша модель для комментариев
from .models import Comment
#встроенная форма для регистрации
from django.contrib.auth.forms import UserCreationForm
#встроенная модель пользователя
from django.contrib.auth.models import User

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment #какая из наших моделей будет использоваться
        fields = ('body',)

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')