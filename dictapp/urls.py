from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("search/", views.search_word, name="search_word"),
    path("my-words/", views.my_words, name="my_words"),
    path("save-word/", views.save_word, name="save_word"),
    path("remove-word/<int:word_id>/", views.remove_word, name="remove_word"),
    path("ngsl/", views.ngsl, name="ngsl"),
    path("nawl/", views.nawl, name="nawl"),
    path('account/settings/', views.account_settings, name='account_settings'),
    path('account/update-profile/', views.update_profile, name='update_profile'),
    path('account/change-password/', views.change_password, name='change_password'),
    path('account/delete/', views.delete_account, name='delete_account'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('phrasal-verbs', views.phrasal_verb, name='phrasal_verb')
]
