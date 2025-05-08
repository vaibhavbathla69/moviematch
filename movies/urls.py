from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('like/', views.like_movie, name='like_movie'),
    path('search/', views.movie_search, name='movie_search'),
    path('filter/', views.genre_filter, name='genre_filter'),
    path('top-rated/', views.top_rated, name='top_rated'),
    path('matches/', views.get_similar_users, name='matches'),
    path('my-likes/', views.my_likes, name='my_likes'),
    # path('signup/', views.SignUpView.as_view(), name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),
    path("recommended/", views.recommended_movies, name="recommended_movies"),
    path('me/', views.my_profile, name='my_profile'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('user/<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
]
