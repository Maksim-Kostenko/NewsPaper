user1 = User.objects.create_user(user = 'user1')
user2 = User.objects.create_user(user = 'user2')

author1 = Author.objects.create(user=user1)
author2 = Author.objects.create(user=user2)

Category.objects.create(name_category='Политика')
Category.objects.create(name_category='Технологии')
Category.objects.create(name_category='Спорт')
Category.objects.create(name_category='Культура')

article1 = Post.objects.create(author=author1, title="Первая статья о политике и технологиях", content="Подробный анализ современных технологий в политике...", type_post ='AR')
article2 = Post.objects.create(author=author2, title="Вторая статья о спорте", content="Новые тенденции в мировом спорте...", type_post='AR')
news1 = Post.objects.create(author=author1, title="Новости культуры", content="Главные культурные события недели...", type_post ='NW')

article1.category.add(Category.objects.get(name_category='Политика'))
article1.category.add(Category.objects.get(name_category='Технологии'))
article2.category.add(Category.objects.get(name_category='Спорт'))
news1.category.add(Category.objects.get(name_category='Культура'))

comment1 = Comment.objects.create(post=article1, user=user1, content="Отличная статья!")
comment2 = Comment.objects.create(post=article1, user=user2, content="Не согласен с автором")
comment3 = Comment.objects.create(post=article2, user=user1, content="Интересный взгляд")
comment4 = Comment.objects.create(post=news1, user=user2, content="Спасибо за новость!")

article1.like()
article1.like()
article2.dislike()
news1.like()
news1.like()

comment1.like()
comment2.dislike()
comment3.like()
comment4.like()

author1.update_rating()
author2.update_rating()

best_author = Author.objects.order_by('-rating').first()
print(f"Username: {best_author.user.username}")
print(f"Рейтинг: {best_author.rating}\n")

best_post = Post.objects.filter(type_post ='AR').order_by('-rating').first()
print(f"Дата: {best_post.date_created}")
print(f"Автор: {best_post.author.user.username}")
print(f"Рейтинг: {best_post.rating}")
print(f"Заголовок: {best_post.title}")
print(f"Превью: {best_post.preview()}\n")

for comment in best_post.comment_set.all().order_by('-date_created'):
    print(f"Дата: {comment.date_created}")
    print(f"Пользователь: {comment.user.username}")
    print(f"Рейтинг: {comment.rating}")
    print(f"Текст: {comment.content}\n")
