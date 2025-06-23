from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum


# Create your models here.
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        post_rating = self.post_set.aggregate(total_sum=Sum('rating'))['total_sum'] or 0
        post_rating *= 3
        comment_rating = self.user.comment_set.aggregate(total_sum=Sum('rating'))['total_sum'] or 0
        comment_rating_author = Comment.objects.filter(post__author=self).aggregate(total_sum=Sum('rating'))['total_sum'] or 0
        self.rating = post_rating + comment_rating + comment_rating_author
        self.save()

class Category(models.Model):
    # CATEGORY_CHOICES = [
    #     ('POL', 'Политика'),
    #     ('ECO', 'Экономика'),
    #     ('SOC', 'Общество'),
    #     ('TEC', 'Технологии'),
    #     ('SCI', 'Наука'),
    #     ('HEA', 'Здоровье'),
    #     ('EDU', 'Образование'),
    #     ('CUL', 'Культура'),
    #     ('SPO', 'Спорт'),
    #     ('INC', 'Происшествия'),
    #     ('AUT', 'Авто'),
    #     ('REA', 'Недвижимость'),
    #     ('TOU', 'Туризм'),
    #     ('ENT', 'Развлечения'),
    #     ('FAS', 'Мода'),
    #     ('FOO', 'Еда'),
    #     ('ECL', 'Экология'),
    #     ('HIS', 'История'),
    #     ('REL', 'Религия'),
    #     ('OTH', 'Другое')
    # ]
    #
    # name_category = models.CharField(unique=True, choices=CATEGORY_CHOICES)

    name_category = models.CharField(max_length=50, unique=True)


class Post(models.Model):

    ARTICLE = 'AR'
    NEWS = 'NW'

    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость')
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255, null=False)
    content = models.TextField(max_length=1000)
    rating = models.IntegerField(default=0)
    type_post = models.CharField(choices=POST_TYPES, default=ARTICLE)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f'{self.content[:123]}...'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    date_created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
