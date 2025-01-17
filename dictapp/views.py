from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
import requests
from .models import Word


def index(request):
    return render(request, 'index.html')


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


def my_words(request):
    word_list = Word.objects.all()
    paginator = Paginator(word_list, 9)

    page = request.GET.get('page')
    words = paginator.get_page(page)

    return render(request, 'my_words.html', {'words': words})


def save_word(request):
    if request.method == 'POST':
        word = request.POST.get('word', '').strip()
        if word:
            try:
                response = requests.get(
                    f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
                if response.status_code == 200:
                    word_data = response.json()[0]
                    if not Word.objects.filter(word=word_data['word']).exists():
                        Word.objects.create(
                            word=word_data['word'],
                            phonetic=word_data.get('phonetic', ''),
                            meanings=word_data.get('meanings', [])
                        )
                    return redirect('my_words')
            except Exception as e:
                pass
    return redirect('search_word')


def remove_word(request, word_id):
    if request.method == 'POST':
        word = get_object_or_404(Word, id=word_id)
        word.delete()
    return redirect('my_words')
