from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Blog, Tag, Comment, Like
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db.models import Count


def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'User Already exists!')
                return redirect('signup')

            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already exists!')
                return redirect('signup')

            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
                user.save()
                return redirect('login')
        else:
            messages.info(request, 'Password not matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('blog_list')
        else:
            messages.info(request, 'Invalid username or password')
            return redirect('login')
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def blog_list(request):
    query = request.GET.get('query')
    if query:
        tags = Tag.objects.filter(name__icontains=query)
        blogs = Blog.objects.filter(tags__in=tags).distinct()
    else:
        blogs = Blog.objects.all()

    paginator = Paginator(blogs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog_list.html', {'page_obj': page_obj, 'query': query})

@login_required(login_url='login')
def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    comments = blog.comments.all()
    for comment in comments:
        comment.liked_by_user = comment.like_set.filter(user=request.user).exists()
    return render(request, 'blog_detail.html', {'blog': blog, 'comments': comments})


@login_required(login_url='login')
def add_comment(request, slug):
    if request.method == 'POST':
        blog = get_object_or_404(Blog, slug=slug)
        content = request.POST.get('content')
        if content:
            comment = Comment.objects.create(blog=blog, user=request.user, content=content)
            return redirect('blog_detail', slug=slug)

    return redirect('blog_detail', slug=slug)


@login_required(login_url='login')
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    
    already_liked = Like.objects.filter(comment=comment, user=request.user).exists()
    
    if already_liked:
        Like.objects.filter(comment=comment, user=request.user).delete()
    else:
        Like.objects.create(comment=comment, user=request.user)
    
    comment.likes = Like.objects.filter(comment=comment).count()
    comment.save()

    return redirect('blog_detail', slug=comment.blog.slug)