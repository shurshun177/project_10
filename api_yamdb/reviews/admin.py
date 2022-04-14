
from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title

# Можно лучше: Как и раньше, заводим все модели в админку.
admin.site.register(Comment)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
