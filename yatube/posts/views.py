from django.core.paginator import Paginator
from .forms import PostForm, CommentForm
from .models import User, Post, Group, Follow
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGINATOR_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.PAGINATOR_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, settings.PAGINATOR_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_amount = posts.count()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=user).exists()
    else:
        following = None
    context = {
        'posts': posts,
        'page_obj': page_obj,
        'author': user,
        'post_amount': post_amount,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    posts_count = post.author.posts.all().count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'posts': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None)
        if form.is_valid():
            post_create = form.save(commit=False)
            post_create.author = request.user
            post_create.save()
            return redirect('posts:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, template, {'form': form, 'is_edit': False})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    post_page = Post.objects.filter(author__following__user=user)
    paginator = Paginator(post_page, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'post_page': post_page,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    if username != request.user.username:
        author_follow = get_object_or_404(User, username=username)
        Follow.objects.get_or_create(user=request.user, author=author_follow)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    followed_author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=followed_author)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', username=username)
