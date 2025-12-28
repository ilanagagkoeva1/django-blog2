from django.urls import path, include
from . import views
#подключение стандартных функций для входа/выхода
from django.contrib.auth import views as auth_views
app_name = 'blog'
#app_name=blog , 
# чтобы в HTML ссылаться на пути как blog:post_list
urlpatterns = [
    #главная страница, где посты блога будут отображаться
    #в файле views.py будет функция post_list
    path('', views.post_list, name='post_list'),
    #страница конкретного поста (детальная)
path('post/<slug:slug>/', views.post_detail, name='post_detail'),
#для обработки лайков через AJAX
path('post/<slug:slug>/like/', views.like_post, name='like_post'),
#стандартные настройки для страницы входа, выхода и смены пароля
path('accounts', include('django.contrib.auth.urls')),
#django.contrib.auth.urls - набор стандартный путей от модуля django
path('register/', views.register, name='register'),
path('comment/<int:pk>/delete/', views.delete_comment, name="delete_comment")
]


