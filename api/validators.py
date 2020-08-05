import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(val):
    # Можно лучше: Стоит валидировать год
    current_year = dt.date.today().year
    if val > current_year:
        raise ValidationError(
            'Год должен быть меньше или равен текущему'
        )
