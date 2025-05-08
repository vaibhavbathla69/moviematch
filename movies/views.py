import requests
from collections import Counter
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import LikedMovie
from .forms import CustomSignUpForm
import random
from .models import UserProfile, Follow
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
def get_liked_movie_ids(user):
    if user.is_authenticated:
        return list(LikedMovie.objects.filter(user=user).values_list('movie_id', flat=True))
    return []

# 🔹 Home Page View
def home(request):
    api_key = settings.TMDB_API_KEY

    # Recent Releases
    recent_url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={api_key}&language=en-US&page=1'
    recent_response = requests.get(recent_url)
    liked_movie_ids = get_liked_movie_ids(request.user)
    recent_movies = recent_response.json().get('results', [])

    # Genre List
    genre_url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=en-US'
    genre_response = requests.get(genre_url)
    genres = genre_response.json().get('genres', [])

    return render(request, 'movies/home.html', {
        'recent_movies': recent_movies,
        'genres': genres,
        'liked_movie_ids': liked_movie_ids
    })


# 🔹 Like Movie
@login_required
def like_movie(request):
    movie_id = request.POST['movie_id']
    title = request.POST['title']
    poster = request.POST['poster']

    # Try to get the like
    liked, created = LikedMovie.objects.get_or_create(
        user=request.user,
        movie_id=movie_id,
        defaults={'movie_title': title, 'movie_poster': poster}
    )

    if not created:
        # Already liked → remove it (unlike)
        liked.delete()
        return JsonResponse({'liked': False})

    return JsonResponse({'liked': True})


# 🔹 My Likes
@login_required
def my_likes(request):
    liked_movies = LikedMovie.objects.filter(user=request.user)
    return render(request, 'movies/my_likes.html', {'liked_movies': liked_movies})


# 🔹 Matchmaking
@login_required
def get_similar_users(request):
    current_user = request.user
    user_liked_movie_ids = set(
        LikedMovie.objects.filter(user=current_user).values_list('movie_id', flat=True)
    )
    match_counter = Counter()

    # Count how many movies other users have in common
    for movie_id in user_liked_movie_ids:
        other_users = LikedMovie.objects.filter(movie_id=movie_id).exclude(user=current_user)
        for other in other_users:
            match_counter[other.user_id] += 1

    matched_users = []
    total_liked = len(user_liked_movie_ids)

    for user_id, shared_count in match_counter.most_common():
        try:
            user = User.objects.get(id=user_id)
            other_user_liked = LikedMovie.objects.filter(user=user).values_list('movie_id', flat=True)
            total_unique = len(set(user_liked_movie_ids).union(other_user_liked))
            match_percent = int((shared_count / total_unique) * 100) if total_unique else 0

            matched_users.append({
                'user': user,
                'match_percent': match_percent,
                'shared_count': shared_count,
                'profile': getattr(user, 'userprofile', None),
            })

        except User.DoesNotExist:
            continue

    # Sort by percentage (optional if using Counter order)
    matched_users.sort(key=lambda u: u['match_percent'], reverse=True)

    return render(request, 'movies/match_list.html', {
        'matches': matched_users
    })


# 🔹 Movie Search
def movie_search(request):
    query = request.GET.get("query")
    if not query:
        return redirect('home')
    
    url = f"https://api.themoviedb.org/3/search/movie?api_key={settings.TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    movies = response.json().get("results", [])
    print(movies)
    liked_movie_ids = get_liked_movie_ids(request.user)

    return render(request, "movies/search_results.html", {
        "movies": movies,
        'liked_movie_ids': liked_movie_ids,
        "query": query
    })


# Genre Filter
def genre_filter(request):
    genre_id = request.GET.get("genre_id")
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={settings.TMDB_API_KEY}&with_genres={genre_id}"
    response = requests.get(url)
    movies = response.json().get("results", [])
    liked_movie_ids = get_liked_movie_ids(request.user)
    return render(request, "movies/genre_results.html", {
        "movies": movies,
        'liked_movie_ids': liked_movie_ids,
        "genre_id": genre_id
    })


#  Top Rated
def top_rated(request):
    url = f'https://api.themoviedb.org/3/movie/top_rated?api_key={settings.TMDB_API_KEY}&language=en-US&page=1'
    response = requests.get(url)
    liked_movie_ids = get_liked_movie_ids(request.user)
    movies = response.json().get('results', [])
    return render(request, 'movies/top_rated.html', {'movies': movies, 'liked_movie_ids': liked_movie_ids,})


#  Logout
def logout_view(request):
    logout(request)
    return redirect('login')


#  Signup
class SignUpView(CreateView):
    form_class = CustomSignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

# movie_detail view 

def movie_detail(request, movie_id):
    api_key = settings.TMDB_API_KEY

    # Movie details
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}"
    reviews_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={api_key}&language=en-US"
    watch_url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}"
    watch_data = requests.get(watch_url).json()
    watch_info = watch_data.get('results', {}).get('US') 
    
    movie = requests.get(movie_url).json()
    credits = requests.get(credits_url).json()
    reviews = requests.get(reviews_url).json()

    #cast and director
    cast = credits.get('cast', [])[:8]  
    crew = credits.get('crew', [])
    director = next((member for member in crew if member.get('job') == 'Director'), None)
    liked_movie_ids = get_liked_movie_ids(request.user)
    # reviews
    reviews_list = reviews.get('results', [])[:3]  # Top 3 reviews

    

    return render(request, "movies/movie_detail.html", {
        "movie": movie,
        "cast": cast,
        "director": director,
        "reviews": reviews_list,
       
        "watch_info": watch_info,
        'liked_movie_ids': liked_movie_ids,
    })


# recommendations view
def recommended_movies(request):
    liked_movies = LikedMovie.objects.filter(user=request.user)
    api_key = settings.TMDB_API_KEY
    recommended = []
    liked_movie_ids = get_liked_movie_ids(request.user)
    for liked in liked_movies:
        movie_id = liked.movie_id
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}&language=en-US&page=1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            recommended.extend(data.get('results', []))

    # Deduplicate by movie ID
    seen_ids = set()
    unique_recommendations = []
    for movie in recommended:
        if movie['id'] not in seen_ids:
            unique_recommendations.append(movie)
            seen_ids.add(movie['id'])

    
    random.shuffle(unique_recommendations)
    top_recommended = unique_recommendations[:12]

    return render(request, "movies/recommended.html", {"recommended": top_recommended, 'liked_movie_ids': liked_movie_ids,})


@login_required
def my_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=profile)

    liked_movies = LikedMovie.objects.filter(user=request.user)

    return render(request, 'movies/my_profile.html', {
        'form': form,
        'liked_movies': liked_movies,
        'profile': profile
    })

def user_profile(request, username):
    user = User.objects.get(username=username)
    profile, _ = UserProfile.objects.get_or_create(user=user)
    liked_movies = LikedMovie.objects.filter(user=user)

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    followers_count = user.followers.count()
    following_count = user.following.count()

    return render(request, 'movies/user_profile.html', {
        'user_profile': profile,
        'liked_movies': liked_movies,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
    })

@login_required
def follow_toggle(request, username):
    target_user = User.objects.get(username=username)

    if target_user != request.user:
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user
            
        )
        print(f"Follow: {follow}, Created: {created}")
        if not created:
            follow.delete()
            return JsonResponse({'follow': False})

    return JsonResponse({'follow': True})
