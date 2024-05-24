from django.urls import path, include
from rest_framework import routers

from blog import views


router = routers.DefaultRouter()


urlpatterns = [
    path("feed", views.PageViewSet.as_view({"get": "feed"}), name="feed"),
    path("tag", views.TagViewSet.as_view({"post": "create"}), name="create_tag"),
    path("tags", views.TagViewSet.as_view({"get": "list"}), name="list_tags"),
    path("page", views.PageViewSet.as_view({"post": "create"}), name="create_page"),
    path(
        "page/<slug:pk>/block",
        views.PageViewSet.as_view({"patch": "block"}),
        name="block_page",
    ),
    path(
        "page/<slug:pk>/follow",
        views.PageViewSet.as_view({"patch": "follow"}),
        name="follow",
    ),
    path(
        "page/<slug:pk>/unfollow",
        views.PageViewSet.as_view({"patch": "unfollow"}),
        name="unfollow",
    ),
    path(
        "page/<slug:pk>/followers",
        views.PageViewSet.as_view({"get": "retrieve_followers"}),
        name="retrieve_followers",
    ),
    path(
        "page/<slug:pk>",
        views.PageViewSet.as_view(
            {"delete": "destroy", "get": "retrieve", "patch": "partial_update"}
        ),
        name="page_crud",
    ),
    path(
        "page/<slug:pk>/post",
        views.PostViewSet.as_view({"post": "create"}),
        name="create_post",
    ),
    path(
        "post/<slug:pk>",
        views.PostViewSet.as_view({"delete": "destroy", "patch": "partial_update"}),
        name="post_delete_and_patch",
    ),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

urlpatterns += router.urls
