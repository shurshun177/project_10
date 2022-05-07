from django.urls import include, path

from .v1 import urls as v1_urls

# Можно лучше: рассказываем про такой способ распределения api по папкам:
# API для v1 в папке v1
# В этой же папке просто подключаем API.
# Если будет v2/ то оно просто создаётся в папке v2 и добавляется сюда через
# include
urlpatterns = [
    path('v1/', include(v1_urls))
]
