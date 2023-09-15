from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

from blog.constants import OBJ_PER_PAGE
from blog.forms import CommentForm, PostForm
from blog.models import Category, Comment, Post, UserModel


def get_query_posts(published=True):
    queryset = Post.objects.prefetch_related(
        'location',
        'author',
        'category').annotate(
            comment_count=Count('comments')).order_by('-pub_date')
    if published:
        return queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
    return queryset


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_id = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_id = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.post_id.pk})


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'slug': self.request.user})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentEditMixin:
    template_name = 'blog/comment.html'
    model = Comment

    def get_success_url(self):
        post = self.object.post
        return reverse_lazy('blog:post_detail', kwargs={'pk': post.id})

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(CommentEditMixin, UpdateView):
    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        post = self.object.post
        return reverse_lazy('blog:post_detail', kwargs={'pk': post.id})


class CommentDeleteView(CommentEditMixin, DeleteView):
    template_name = 'blog/comment.html'
    model = Comment

    def get_success_url(self):
        post = self.object.post
        return reverse_lazy('blog:post_detail', kwargs={'pk': post.id})


class PostEditMixin:
    template_name = 'blog/create.html'
    model = Post

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(PostEditMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('blog:edit_post', kwargs={'pk': self.kwargs['pk']})


class PostDeleteView(PostEditMixin, DeleteView):
    success_url = reverse_lazy('blog:index')


class ProfileListView(ListView):
    template_name = 'blog/profile.html'
    model = Post
    paginate_by = OBJ_PER_PAGE

    def get_queryset(self):
        username = self.kwargs['slug']
        if self.kwargs['slug'] == self.request.user.username:
            return get_query_posts(published=False).filter(
                author__username=username)
        return get_query_posts().filter(
            author__username=username)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(UserModel,
                                               username=self.kwargs['slug'])
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('blog:edit_profile')

    def get_object(self):
        return UserModel.objects.get(username=self.request.user)


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    queryset = get_query_posts()
    paginate_by = OBJ_PER_PAGE


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = {}
        if self.get_object().author != self.request.user:
            context['post'] = get_object_or_404(
                get_query_posts(), pk=self.kwargs['pk']
            )
        else:
            context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (self.object.comments.select_related('author'))
        return context


class CategoryListView(ListView):
    template_name = 'blog/category.html'
    paginate_by = OBJ_PER_PAGE

    def get_queryset(self):
        return get_query_posts().filter(
            category__slug=self.kwargs['slug'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category,
                                                is_published=True,
                                                slug=self.kwargs['slug'])
        return context
