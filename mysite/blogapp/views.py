from django.contrib.gis.feeds import Feed
from django.views.generic import ListView
from rest_framework.reverse import reverse_lazy

from .models import Article


class ArticlesListView(ListView):
    model = Article
    template_name = 'blogapp/article_list.html'
    context_object_name = 'articles'
    queryset = (Article.objects
                .select_related('author', 'category')
                .prefetch_related('tags')
                .defer('content'))


class LatestArticlesView(Feed):
    title = "Latest Articles"
    description = "Latest Articles"
    link = reverse_lazy('blogapp:articles')

    def items(self):
        return Article.objects.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content[:200]