import re
from unicodedata import category

from django.core.management.base import BaseCommand

from news.models import Category, Post

class Command(BaseCommand):
    help = ('Позволяет удалять все новости выбранной категории, '
            'при этом необходимо подтвердить действие в терминале')

    def add_arguments(self, parser):
        parser.add_argument('--category',
                            type=str,
                            help='Название категории для удаления новостей',)

    def handle(self, *args, **options):
        category_names = Category.objects.values_list('name_category', flat=True)

        self.stdout.write(f'Доступные категории: {", ".join(category_names)}')

        # Если категория передана как аргумент
        if options['category']:
            category_name = options['category']
        else:
            category_name = input('Введите название категории: ')

        try:
            # Находим категорию в базе данных
            category = Category.objects.get(name_category=category_name)

            # Подсчитываем количество постов для удаления
            posts_count = Post.objects.filter(category=category).count()

            if posts_count == 0:
                self.stdout.write(
                    self.style.WARNING(f'В категории "{category_name}" нет новостей')
                )
                return

            self.stdout.write(
                f'Вы действительно хотите удалить {posts_count} '
                f'новостей из категории "{category_name}"? (yes/no)'
            )

            confirmation = input().strip()
            # Удаляем все не-буквенные символы и приводим к нижнему регистру
            confirmation_clean = re.sub(r'[^a-zA-Zа-яА-Я]', '', confirmation).lower()

            if confirmation_clean in ['yes', 'y', 'да', 'д']:
                deleted_count = Post.objects.filter(category=category).delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно удалено {deleted_count[0]} новостей из категории "{category_name}"'
                    )
                )
            else:
                self.stdout.write('Удаление отменено')

        except Category.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Категория "{category_name}" не найдена')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Произошла ошибка: {e}')
            )