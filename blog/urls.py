from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name="signup"),
    path('login', views.login_user, name="login"),
    path('logout', views.logout_user, name='logout'),
    path('', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),

]