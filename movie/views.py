from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie

import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64
from collections import Counter

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

def home(request):
    #return HttpResponse('<h1>Welcome to Home Page</h1>')
    #return render(request, 'home.html')
    #return render(request, 'home.html', {'name':'Alejandro Sepuleda Posada'})
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies': movies})

def about(request):
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email':email})