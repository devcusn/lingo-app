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
from .models import Word, WordUser
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta


def index(request):
    # Redirect to dashboard if user is logged in
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')


def login_view(request):
    # Redirect to dashboard if user is already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Changed from 'index' to 'dashboard'
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')


def register_view(request):
    # Redirect to dashboard if user is already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')

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
        return redirect('dashboard')  # Changed from 'index' to 'dashboard'

    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('index')


def search_word(request):
    if request.method == 'POST':
        # Convert to lowercase for consistency
        word = request.POST.get('word', '').strip().lower()
        if word:
            try:
                # First, try to find the word in our database
                existing_word = Word.objects.filter(word__iexact=word).first()

                if existing_word:
                    # Word found in database, return it directly
                    return render(request, 'search_word.html', {
                        'word_data': {
                            'word': existing_word.word,
                            'phonetic': existing_word.phonetic,
                            'meanings': existing_word.meanings
                        }
                    })

                # If word not found in database, fetch from API
                response = requests.get(
                    f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')

                if response.status_code == 200:
                    word_data = response.json()[0]

                    # Save the word to our database
                    Word.objects.create(
                        word=word_data['word'],
                        phonetic=word_data.get('phonetic', ''),
                        meanings=word_data.get('meanings', [])
                    )

                    return render(request, 'search_word.html', {'word_data': word_data})
                else:
                    return render(request, 'search_word.html', {'error': 'Word not found'})

            except Exception as e:
                return render(request, 'search_word.html', {'error': 'An error occurred while fetching the word'})

    return render(request, 'search_word.html')


@login_required(login_url='login')
def my_words(request):
    search_query = request.GET.get('q', '').strip()
    word_users = WordUser.objects.filter(user=request.user)

    if search_query:
        word_users = word_users.filter(word__word__icontains=search_query)

    paginator = Paginator(word_users, 9)
    page = request.GET.get('page')
    words = paginator.get_page(page)

    return render(request, 'my_words.html', {
        'words': words,
        'search_query': search_query
    })


@login_required(login_url='login')
def save_word(request):
    if request.method == 'POST':
        word_text = request.POST.get('word', '').strip()
        if word_text:
            try:
                response = requests.get(
                    f'https://api.dictionaryapi.dev/api/v2/entries/en/{word_text}')
                if response.status_code == 200:
                    word_data = response.json()[0]
                    # Get or create the word
                    word, created = Word.objects.get_or_create(
                        word=word_data['word'],
                        defaults={
                            'phonetic': word_data.get('phonetic', ''),
                            'meanings': word_data.get('meanings', [])
                        }
                    )
                    # Create the word-user relationship if it doesn't exist
                    WordUser.objects.get_or_create(
                        word=word,
                        user=request.user
                    )
                    return redirect('my_words')
            except Exception as e:
                pass
    return redirect('search_word')


@login_required(login_url='login')
def remove_word(request, word_id):
    if request.method == 'POST':
        WordUser.objects.filter(word_id=word_id, user=request.user).delete()
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


@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password_confirm')
        user = request.user

        # Verify password
        if not user.check_password(password):
            messages.error(request, 'Incorrect password.')
            return redirect('account_settings')

        try:
            # Delete all user's words
            WordUser.objects.filter(user=user).delete()
            # Delete the user
            user.delete()
            messages.success(
                request, 'Your account has been successfully deleted.')
            return redirect('index')
        except Exception as e:
            messages.error(
                request, 'An error occurred while deleting your account.')
            return redirect('account_settings')

    return redirect('account_settings')


@login_required
def dashboard(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Get word counts using WordUser model
    total_words = WordUser.objects.filter(user=request.user).count()
    words_this_week = WordUser.objects.filter(
        user=request.user,
        created_at__gte=week_ago
    ).count()
    words_today = WordUser.objects.filter(
        user=request.user,
        created_at__gte=today_start
    ).count()

    # Determine language level based on word count
    def get_language_level(word_count):
        if word_count < 1000:
            return {
                'level': 'A1',
                'description': 'Beginner',
                'progress': (word_count / 1000) * 100,
                'next_level': 1000 - word_count,
                'color': 'bg-info'
            }
        elif word_count < 2000:
            return {
                'level': 'A2',
                'description': 'Elementary',
                'progress': ((word_count - 1000) / 1000) * 100,
                'next_level': 2000 - word_count,
                'color': 'bg-info'
            }
        elif word_count < 3500:
            return {
                'level': 'B1',
                'description': 'Intermediate',
                'progress': ((word_count - 2000) / 1500) * 100,
                'next_level': 3500 - word_count,
                'color': 'bg-success'
            }
        elif word_count < 5000:
            return {
                'level': 'B2',
                'description': 'Upper-Intermediate',
                'progress': ((word_count - 3500) / 1500) * 100,
                'next_level': 5000 - word_count,
                'color': 'bg-success'
            }
        elif word_count < 8000:
            return {
                'level': 'C1',
                'description': 'Advanced',
                'progress': ((word_count - 5000) / 3000) * 100,
                'next_level': 8000 - word_count,
                'color': 'bg-warning'
            }
        else:
            return {
                'level': 'C2',
                'description': 'Proficiency',
                'progress': 100,
                'next_level': 0,
                'color': 'bg-danger'
            }

    language_level = get_language_level(total_words)

    # Get recent words using WordUser model
    recent_words = WordUser.objects.filter(
        user=request.user
    ).select_related('word').order_by('-created_at')[:5]

    context = {
        'total_words': total_words,
        'words_this_week': words_this_week,
        'words_today': words_today,
        'recent_words': recent_words,
        'language_level': language_level,
    }

    return render(request, 'dashboard.html', context)


@login_required
def phrasal_verb(request):
    return render(request, 'phrasal-verb.html')
