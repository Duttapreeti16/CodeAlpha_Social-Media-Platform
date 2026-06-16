import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.contrib.auth.forms import AuthenticationForm

from .models import User, Post, Comment, Like
from .forms import CustomUserCreationForm, PostForm, CommentForm

def index(request):
    if request.user.is_authenticated:
        # Get posts from followed users and own posts
        following_users = request.user.following.all()
        posts = Post.objects.filter(author__in=following_users) | Post.objects.filter(author=request.user)
        posts = posts.distinct().order_by('-created_at')
        # If no posts (brand new user), maybe show all?
        if not posts.exists():
             posts = Post.objects.all().order_by('-created_at')[:50]
    else:
        posts = Post.objects.all().order_by('-created_at')[:50]

    if request.method == 'POST' and request.user.is_authenticated:
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            new_post = post_form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    "success": True,
                    "post": {
                        "id": new_post.id,
                        "author": new_post.author.username,
                        "content": new_post.content,
                        "created_at": new_post.created_at.strftime("%b %d, %Y %I:%M %p"),
                        "likes_count": 0,
                        "comments_count": 0,
                        "image_url": new_post.image.url if new_post.image else None
                    }
                })
            return redirect('index')
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "error": "Invalid post"})
    else:
        post_form = PostForm()
    
    suggested_users = User.objects.exclude(username=request.user.username)[:5] if request.user.is_authenticated else User.objects.all()[:5]
    liked_post_ids = set(request.user.likes.values_list('post_id', flat=True)) if request.user.is_authenticated else set()
    following_usernames = set(request.user.following.values_list('username', flat=True)) if request.user.is_authenticated else set()
    return render(request, "network/index.html", {
        "posts": posts,
        "post_form": post_form,
        "comment_form": CommentForm(),
        "suggested_users": suggested_users,
        "liked_post_ids": liked_post_ids,
        "following_usernames": following_usernames,
    })

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = request.user.following.filter(username=username).exists()

    liked_post_ids = set(request.user.likes.values_list('post_id', flat=True)) if request.user.is_authenticated else set()
    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "is_following": is_following,
        "followers_count": profile_user.followers.count(),
        "following_count": profile_user.following.count(),
        "liked_post_ids": liked_post_ids,
    })

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    else:
        form = AuthenticationForm()
    return render(request, "network/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("index")

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = CustomUserCreationForm()
    return render(request, "network/register.html", {"form": form})

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                "success": True,
                "comment": {
                    "id": comment.id,
                    "author": comment.author.username,
                    "content": comment.content,
                    "created_at": comment.created_at.strftime("%b %d, %Y %I:%M %p")
                }
            })
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"success": False, "error": "Invalid comment"})
    
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like = Like.objects.filter(post=post, user=request.user).first()
    
    if like:
        like.delete()
        liked = False
    else:
        Like.objects.create(post=post, user=request.user)
        liked = True
        
    return JsonResponse({
        "liked": liked,
        "like_count": post.likes.count()
    })

@login_required
@require_POST
def toggle_follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user == user_to_follow:
        return JsonResponse({"error": "You cannot follow yourself"}, status=400)
        
    if request.user.following.filter(username=username).exists():
        request.user.following.remove(user_to_follow)
        following = False
    else:
        request.user.following.add(user_to_follow)
        following = True
        
    return JsonResponse({
        "following": following,
        "followers_count": user_to_follow.followers.count()
    })
