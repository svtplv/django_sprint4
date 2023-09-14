from django.urls import include, path

from blog import views

app_name = 'blog'

posts_urls = [
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('<int:pk>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('<int:pk>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('<int:pk>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('<int:id>/edit_comment/<int:pk>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('<int:id>/delete_comment/<int:pk>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
]

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/', include(posts_urls)),
    path('profile/<slug:slug>/', views.ProfileListView.as_view(),
         name='profile'),
    path('edit_profile/', views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('category/<slug:slug>/', views.CategoryListView.as_view(),
         name='category_posts'),
]
