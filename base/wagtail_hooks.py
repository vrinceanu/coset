import django_filters
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.ui.tables import Column, DateColumn
from wagtail.admin.ui.tables.pages import PageStatusColumn, PageTitleColumn
from wagtail import hooks
from .models import PostPage, PostSectionPage, CATEGORY_CHOICES

class PostPageFilterSet(django_filters.FilterSet):
    # This creates a dropdown filter for the Category ForeignKey
    category = django_filters.ChoiceFilter(
        choices=CATEGORY_CHOICES,
        label="Category",
        empty_label="All Categories"
    )

    class Meta:
        model = PostPage
        fields = ['category']

class PostPageViewSet(PageListingViewSet):
    model = PostPage
    icon = "doc-full"
    menu_label = "Posts"
    menu_name = "all_posts"
    add_to_admin_menu = True  # Creates the separate sidebar menu item
    menu_order = 200  # Position in the sidebar
    
    filterset_class = PostPageFilterSet
    search_fields = ("title", "category")

    columns = [
        PageTitleColumn("title", label="Title", sort_key="title"),
        Column("category", label="Category", sort_key="category"), 
        DateColumn("first_published_at", label="Published Date"),
        PageStatusColumn("status", label="Status"),
    ]


@hooks.register("register_admin_viewset")
def register_post_page_viewset():
    return PostPageViewSet("posts")

@hooks.register('construct_explorer_page_queryset')
def exclude_posts_from_explorer(parent_page, pages, request):
    # This prevents PostPage from appearing in the standard page tree
    # but they will still appear in your custom "All Posts" ViewSet.
    return pages.not_type(PostSectionPage)