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

"""
"user": Saddam, 
"token": 
(
"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIj
oiYWNjZXNzIiwiZXhwIjoxNzAyNzQ5NDk3LCJpYXQiOjE2NzEyMTM0OT
csImp0aSI6ImZjMzYxODFlODYxZTQyOTA4Njg4ZGViOTRhZjk5MWJiIi
widXNlcl9pZCI6MX0.luZxGNc8zahUXpgYQ7upIM7RbsMDhGpC7i9DjRb98P8"
"""
