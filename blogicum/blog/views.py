from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from blog.forms import PostForm, CommentForm
from blog.models import Category, Post, UserModel, Comment


QUERYSET = Post.objects.select_related(
    'location',
    'author',
    'category').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True).annotate(comment_count=Count('comments'))


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'slug': self.request.user})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        post = self.object.post
        return reverse_lazy('blog:post_detail', kwargs={'pk': post.id})

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            get_object_or_404(Comment, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'blog/comment.html'
    model = Comment

    def get_success_url(self):
        post = self.object.post
        return reverse_lazy('blog:post_detail', kwargs={'pk': post.id})

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            get_object_or_404(Comment, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('blog:edit_post', kwargs={'pk': self.kwargs['pk']})

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'blog/create.html'
    model = Post
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


class ProfileListView(ListView):
    template_name = 'blog/profile.html'
    model = Post

    def get_queryset(self):
        if self.kwargs['slug'] == self.request.user.username:
            return super().get_queryset().select_related(
                'location', 'author', 'category').filter(
                    author__username=self.request.user.username).annotate(
                        comment_count=Count('comments')).order_by('-pub_date')
        return QUERYSET.filter(author__username=self.kwargs['slug']).order_by(
            '-pub_date')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(UserModel,
                                               username=self.kwargs['slug'])
        return context
    paginate_by = 10


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('blog:edit_profile')

    def get_object(self):
        return UserModel.objects.get(username=self.request.user)


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    ordering = ['-pub_date']
    queryset = QUERYSET
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = {}
        if self.get_object().author != self.request.user:
            context['post'] = get_object_or_404(QUERYSET, pk=self.kwargs['pk'])
        else:
            context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (self.object.comments.select_related('author'))
        return context


class CategoryListView(ListView):
    template_name = 'blog/category.html'

    def get_queryset(self):
        return QUERYSET.filter(category__slug=self.kwargs['slug']).order_by(
            '-pub_date')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category,
                                                is_published=True,
                                                slug=self.kwargs['slug'])
        return context
    paginate_by = 10
