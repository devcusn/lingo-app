from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search_word, name="search_word"),
    path("my-words/", views.my_words, name="my_words"),
    path("save-word/", views.save_word, name="save_word"),
    path("remove-word/<int:word_id>/", views.remove_word, name="remove_word"),
]
