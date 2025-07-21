
from django.urls import path


from news.views import NewsList, NewsDetail, PostCreated, PostDelete, PostUpdate, NewsListSearch, CategorySubscribe

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('search/', NewsListSearch.as_view(), name='news_list_search'),
    path('<int:pk>/', NewsDetail.as_view(), name='news_detail'),

    #Новости
    path('create/', PostCreated.as_view(), name='news_create'),
    path('<int:pk>/update/', PostUpdate.as_view(), name='news_update'),
    path('<int:pk>/delete', PostDelete.as_view(), name='news_delete'),

    #Статьи
    path('article/create/', PostCreated.as_view(), name='article_create'),
    path('article/<int:pk>/update/', PostUpdate.as_view(), name='article_update'),
    path('article/<int:pk>/delete', PostDelete.as_view(), name='article_delete'),

    path('subscribe/', CategorySubscribe.as_view(), name = 'category_subscribe')
]
