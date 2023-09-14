from django.db.models import Count
from django.utils import timezone

from blog.models import Post


def get_query_posts(published=True):
    queryset = Post.objects.prefetch_related(
            'location',
            'author',
            'category').annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
    if published:
        return queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
    return queryset
