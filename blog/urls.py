from django.urls import path

from .views import (
    CategoryPostListView,
    NoteCollectionListView,
    NoteCollectionView,
    NoteDetailView,
    NoteListView,
    PostDetailView,
    PostListView,
    TagPostListView,
    MemoryDetailView,
    TimelineView,
    ThoughtListView,
)

app_name = "blog"

urlpatterns = [
    path(
        "",
        PostListView.as_view(),
        name="post_list",
    ),
    path(
        "category/<slug:slug>/",
        CategoryPostListView.as_view(),
        name="category_post_list",
    ),
    path(
        "tag/<slug:slug>/",
        TagPostListView.as_view(),
        name="tag_post_list",
    ),

    # 手记
    path(
        "notes/",
        NoteListView.as_view(),
        name="note_list",
    ),
    path(
        "notes/collections/",
        NoteCollectionListView.as_view(),
        name="note_collection_list",
    ),
    path(
        "notes/collection/<slug:slug>/",
        NoteCollectionView.as_view(),
        name="note_collection",
    ),
    path(
        "notes/<slug:slug>/",
        NoteDetailView.as_view(),
        name="note_detail",
    ),
    path(
        "timeline/",
        TimelineView.as_view(),
        name="timeline",
    ),
    path(
        "memories/<slug:slug>/",
        MemoryDetailView.as_view(),
        name="memory_detail",
    ),
    path(
        "thoughts/",
        ThoughtListView.as_view(),
        name="thought_list",
    ),
    # 必须放在最后，避免截获前面的固定路径
    path(
        "<slug:slug>/",
        PostDetailView.as_view(),
        name="post_detail",
    ),
]
