from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import requests
import csv
import os
from .models import Word
from django.contrib import messages


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
    search_query = request.GET.get('q', '').strip()
    word_list = Word.objects.filter(user=request.user)

    if search_query:
        # Only search in the word field for SQLite compatibility
        word_list = word_list.filter(word__icontains=search_query)

    paginator = Paginator(word_list, 9)
    page = request.GET.get('page')
    words = paginator.get_page(page)

    return render(request, 'my_words.html', {
        'words': words,
        'search_query': search_query
    })


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


def ngsl(request):
    return render(request, 'new-general-service-list.html')


def nawl(request):
    search_query = request.GET.get('q', '').strip()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'nawl.csv')

    words = []
    with open(csv_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if not search_query or search_query.lower() in row['Headword'].lower():
                words.append(row)

    paginator = Paginator(words, 50)  # Show 50 words per page
    page = request.GET.get('page')
    words_page = paginator.get_page(page)

    return render(request, 'new-academic-word-list.html', {
        'words': words_page,
        'search_query': search_query
    })


@login_required
def account_settings(request):
    return render(request, 'account_settings.html')


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Check if username is already taken
        if User.objects.exclude(pk=user.pk).filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('account_settings')

        # Check if email is already taken
        if User.objects.exclude(pk=user.pk).filter(email=email).exists():
            messages.error(request, 'Email is already taken.')
            return redirect('account_settings')

        user.username = username
        user.email = email
        user.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('account_settings')


@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('account_settings')

        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect('account_settings')

        if len(new_password1) < 8:
            messages.error(
                request, 'Password must be at least 8 characters long.')
            return redirect('account_settings')

        request.user.set_password(new_password1)
        request.user.save()
        update_session_auth_hash(request, request.user)  # Keep user logged in
        messages.success(request, 'Password changed successfully.')
        return redirect('account_settings')
