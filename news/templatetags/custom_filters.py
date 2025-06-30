from django import template
import re

register = template.Library()

UNWANTED_WORDS = {
    "политика",
    'новость',
    'статья'
}

@register.filter()
def censor(value:str):
    """
    Фильтр выполняет поиск полных слов из UNWANTED_WORDS,
    если он находит совпадения, то все слова заменяет на *.
    При этом фильтр не учитывает то, что слово может быть с другим окончанием
    :param value: str
    :return: value: str
    """

    if not isinstance(value, str):
        return str(value)

    res = []
    words = re.findall(r'(\w+|\s+|\W+)', value)
    for word in words:
        if word.strip().lower() in UNWANTED_WORDS:
            res.append('*'*len(word))
        else:
            res.append(word)
    return ''.join(res)
