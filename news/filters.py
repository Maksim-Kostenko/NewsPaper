from django_filters import FilterSet, DateFilter, DateFromToRangeFilter
from django import forms

from news.models import Post

class NewsFilter(FilterSet):
    date_created = DateFilter(
        field_name='date_created',  # имя поля в модели
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Выберите дату',
    )

    class Meta:
        model = Post
        fields = ['title',
                  'author',
                  'date_created',
                  ]

