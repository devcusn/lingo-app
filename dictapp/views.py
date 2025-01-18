from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import requests
from .models import Word


def index(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already exists'})

        user = User.objects.create_user(
            username=username, email=email, password=password1)
        login(request, user)
        return redirect('index')

    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('index')


def search_word(request):
    if request.method == 'POST':
        word = request.POST.get('word', '').strip()
        if word:
            try:
                response = requests.get(
                    f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
                if response.status_code == 200:
                    word_data = response.json()[0]
                    return render(request, 'search_word.html', {'word_data': word_data})
                else:
                    return render(request, 'search_word.html', {'error': 'Word not found'})
            except Exception as e:
                return render(request, 'search_word.html', {'error': 'An error occurred while fetching the word'})
    return render(request, 'search_word.html')


@login_required(login_url='login')
def my_words(request):
    word_list = Word.objects.filter(user=request.user)
    paginator = Paginator(word_list, 9)

    page = request.GET.get('page')
    words = paginator.get_page(page)

    return render(request, 'my_words.html', {'words': words})


@login_required(login_url='login')
def save_word(request):
    if request.method == 'POST':
        word = request.POST.get('word', '').strip()
        if word:
            try:
                response = requests.get(
                    f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
                if response.status_code == 200:
                    word_data = response.json()[0]
                    if not Word.objects.filter(word=word_data['word'], user=request.user).exists():
                        Word.objects.create(
                            user=request.user,
                            word=word_data['word'],
                            phonetic=word_data.get('phonetic', ''),
                            meanings=word_data.get('meanings', [])
                        )
                    return redirect('my_words')
            except Exception as e:
                pass
    return redirect('search_word')


@login_required(login_url='login')
def remove_word(request, word_id):
    if request.method == 'POST':
        word = get_object_or_404(Word, id=word_id, user=request.user)
        word.delete()
    return redirect('my_words')
