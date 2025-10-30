from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie

import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64
from collections import Counter
from dotenv import load_dotenv
import os

def statistics_view(request):
    matplotlib.use('Agg')

    # -------- Gráfica 1: Películas por año --------
    years = Movie.objects.values_list('year', flat=True).distinct().order_by('year')
    movie_counts_by_year = {}
    for year in years:
        if year:
            movies_in_year = Movie.objects.filter(year=year)
        else:
            movies_in_year = Movie.objects.filter(year__isnull=True)
            year = "None"
        count = movies_in_year.count()
        movie_counts_by_year[year] = count

    plt.figure(figsize=(8, 4))
    bar_positions = range(len(movie_counts_by_year))
    plt.bar(bar_positions, movie_counts_by_year.values(), width=0.5, align='center')
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    graphic_years = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # -------- Gráfica 2: Películas por género (solo primer género) --------
    genres = []
    for movie in Movie.objects.values_list('genre', flat=True):
        if movie:  
            first_genre = movie.split(",")[0].strip()
            genres.append(first_genre)

    genre_counts = Counter(genres)

    plt.figure(figsize=(8, 4))
    bar_positions = range(len(genre_counts))
    plt.bar(bar_positions, genre_counts.values(), width=0.5, align='center', color="orange")
    plt.title('Movies per genre (first genre only)')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, genre_counts.keys(), rotation=90)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    graphic_genres = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return render(request, 'statistics.html', {
        'graphic_years': graphic_years,
        'graphic_genres': graphic_genres
    })

# Create your views here.

import numpy as np
from django.shortcuts import render
from movie.models import Movie
from openai import OpenAI

load_dotenv('openAI.env')
client = OpenAI(api_key=os.environ.get('openai_apikey'))

def get_embedding(text):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def home(request):
    searchTerm = request.GET.get('searchMovie')  # lo que escribe el usuario
    recommended_movie = None  

    if searchTerm:
        # 1. Obtener embedding del prompt del usuario
        prompt_embedding = get_embedding(searchTerm)

        # 2. Recorrer películas y calcular similitud
        best_score = -1
        for movie in Movie.objects.all():
            if movie.emb:  # asumimos que está guardado como lista/array
                movie_embedding = np.frombuffer(movie.emb, dtype=np.float32)
                score = cosine_similarity(prompt_embedding, movie_embedding)

                if score > best_score:
                    best_score = score
                    recommended_movie = movie

    return render(request, 'home.html', {
        'searchTerm': searchTerm,
        'recommended_movie': recommended_movie,
    })


def about(request):
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email':email})