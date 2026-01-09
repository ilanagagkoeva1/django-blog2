from django.shortcuts import render, get_object_or_404, redirect
#декоратор для ограничения доступа, т.е. пока пользователь
#не зашел в аккаунт, то он не сможет лайкать посты, оставлять комментарии и т.д.
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse 
#для ответов в формате JSON на AJAX
from django.contrib.auth import login 
#функция login для входа в аккаунт
from .models import Post, Like, Comment 
#наши модели Пост, Лайк и Комментарий
#TODO: добавить формы для комментариев и регистрации
from .forms import CommentForm, RegisterForm #наши формы из файла forms.py
#импорт форм для комментариев и регистрации
from django.contrib.auth.models import User
#импорт модели Пользователя
from django.contrib.auth.forms import UserCreationForm
#импорт стандартной формы для регистрации
from django.contrib import messages 
# модуль для вывода сообщений пользователю
from django.db.models import Q

def post_list(request):
    posts = Post.objects.filter(published=True)
    #получаем из базы все посты, которые опубликованы
    #черновики игнорируем
    #третий аргумент - словарь, где хранятся данные доступные в HTML
    query = request.GET.get('q')
    # query = query.lower()
    # Поправить поиск с учетом регистра
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(body__icontains=query)
        )
    return render(request, 'blog/post_list.html', {'posts': posts, 'query': query})
# Create your views here.
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    #пробуем найти пост по слагу, если его нет, то выдаем ошибку 404
    #проверяем, что пост опубликован
    comments = post.comments.filter(active=True) 
    #комментарии привязанные к конкретному посту, которые активны
    #TODO: обработка формы для нового комментария
    if request.method == 'POST':
        form = CommentForm(request.POST)
        #создаем экземпляр формы, передаем данные которые ввел пользователь
        #т.е. текст комментария
        if form.is_valid():
            #проверяем, что данные корректны, например, что комментарий не пустой
            comment = form.save(commit=False)
            #сохраняем текст комментария, но не в базу, а временно в переменную
            #зачем? чтобы привязать его к посту и к пользователю, а потом
            #сохранить в базу
            comment.post = post #привязываем комментарий к посту
            comment.author = request.user #привязываем комментарий к пользователю

            comment.save() #сохраняем в базу
            #возвращаем пользователя обратно, чтобы избежать
            #дублирования комментариев (повторной отправки формы)
            messages.success(request, "Ваш комментарий на модерации") 

            return redirect('blog:post_detail', slug=post.slug)
    else:
        #если GET-запрос, то создаем пустую форму (сбрасываем данные)
        form = CommentForm()
    return render(request, 'blog/post_detail.html', 
    {'post': post, 'comments': comments})


@login_required
#проверка на вход в аккаунт
def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    user = request.user
    like, created = Like.objects.get_or_create(post=post, user=user)
    #функция get_or_create возвращает кортеж из 2 объектов
    #like - объект
    #created = True, если объект создан, False - если объект уже существует
    if not created:
        #если лайк уже стоял, то удаляем его
        like.delete()
        liked = False
    else:
        liked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes.count()
        })

    return redirect('blog:post_detail', slug=slug)

#TODO: для формы регистрации
def register(request): #создаем метод для формы регистрации
    if request.method == 'POST': #если пользователь нажал на кнопку "зарегистрироваться"
        form = RegisterForm(request.POST) #получаем данные из формы
        if form.is_valid(): #если данные в форме корректны
            user = form.save() #сохраняем пользователя в базу
            login(request, user) #сразу выполняем за него вход
            #чтобы ему не пришлось это делать вручную
            return redirect('blog:edit_profile')
            #перенеправляем на главную страницу
    else: #иначе - если он просто зашел на страницу, форма должна быть пустой
        form = RegisterForm() #или если он повторно зашел
    #показываем страницу регистрации с пустой формой или с ошибками
    return render(request, 'blog/register.html', {'form': form})
# Функция для вывода сообщения после отправки формы и проверки данных




@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_slug = comment.post.slug
    comment.delete()
    return redirect('blog:post_detail', slug=post_slug)

@login_required #только для тех, кто вошел в аккаунт
def like_comment(request, pk): #добавляем функцию, т.е. возможность ставить лайки
    comment = get_object_or_404(Comment, pk=pk) #получаем комментарий на который
    # ставят лайк
    if request.user != comment.author: #если это чужой комментарий, не его
        if request.user in comment.likes.all(): #смотрим, он уже ставил лайк или нет?
            comment.likes.remove(request.user)
            liked = False #удаляем его лайк
        else: #если еще не ставил лайк
            comment.likes.add(request.user)
            liked = True #то добавляем его во множество
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': comment.likes.count()
        })
    
    return redirect('blog:post_detail', slug=comment.post.slug) 
    #возвращаемся на ту же самую страницу

from .forms import ProfileForm
@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            if request.FILES.get('avatar'):
                print("Имя файла:", request.FILES['avatar'].name)
            form.save()
            profile.refresh_from_db()
            print("ПУТЬ:", profile.avatar.path)
            return redirect('blog:dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'blog/edit_profile.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'blog/dashboard.html')

