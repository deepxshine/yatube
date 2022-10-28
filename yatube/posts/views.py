from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow

note_number = 10


def pag(req, post):
    paginator = Paginator(post, note_number)
    page_number = req.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    """передаёт в шаблон posts/index.html десять последних объектов модели
    Post
    """

    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = pag(request, post_list)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """передаёт в шаблон posts/group_list.html десять последних объектов
    модели Post"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    page_obj = pag(request, posts)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = pag(request, post_list)
    template = 'posts/profile.html'
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template = 'posts/post_detail.html'
    form = CommentForm()
    comments = post.post_comments.all()
    context = {
        'post': post,
        'requser': request.user,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('posts:profile', create_post.author)
    template = 'posts/create_post.html'
    context = {'form': form}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    editing_post = get_object_or_404(Post, id=post_id)
    if request.user != editing_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=editing_post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    template = 'posts/create_post.html'
    context = {'form': form, 'is_edit': True}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user, author=author)
    if follow.exists():
        follow.delete()
    return redirect('posts:profile', author)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = pag(request, post_list)
    follow = True
    if post_list.count() == 0:
        follow = False
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
        'follow': follow
    }
    return render(request, template, context)
