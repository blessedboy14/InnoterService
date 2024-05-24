from django.utils import timezone
from django.core.paginator import Paginator
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from blog.authentication import CustomJWTAuthentication
from blog.models import Post, Page, Tag, Followers
from blog.permissions import IsAdminModerCreatorOrReadOnly, IsCreator
from blog.serializers import (
    PostSerializer,
    PageSerializer,
    TagSerializer,
    PageDetailSerializer,
    PaginationParamsSerializer,
    PaginationAndFiltersSerializer,
    FollowerSerializer,
    FollowerResponseSerializer,
)


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all().order_by("-created_at")
    serializer_class = PageSerializer
    permission_classes = [IsAdminModerCreatorOrReadOnly]
    authentication_classes = [CustomJWTAuthentication]
    save_actions = ("create_page", "retrieve", "follow", "unfollow")

    def get_permissions(self):
        if self.action in self.save_actions:
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == "partial_update":
            self.permission_classes = [IsCreator]
        else:
            self.permission_classes = [IsAdminModerCreatorOrReadOnly]
        return [permission() for permission in self.permission_classes]

    def retrieve(self, request, *args, **kwargs):
        page = self.get_object()
        if not page.is_blocked:
            page_number = request.query_params.get("page", 1)
            limit = request.query_params.get("limit", 30)
            params_serializer = PaginationParamsSerializer(data=request.query_params)
            params_serializer.is_valid(raise_exception=True)
            posts = page.posts.all()
            paginator = Paginator(posts, limit)
            items = paginator.page(page_number).object_list
            serializer = PageDetailSerializer(page)
            serializer.posts = items
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"message": "Oops, page is blocked!"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def retrieve_followers(self, request, *args, **kwargs):
        page = self.get_object()
        followers = Followers.objects.filter(page_id=page.id)
        serializer = FollowerResponseSerializer(followers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def follow(request, *args, **kwargs):
        if not Followers.objects.filter(page_id=kwargs["pk"]).exists():
            user_id = request.user.user_id
            response_data = {}
            data = {"page_id": kwargs["pk"]}
            serializer = FollowerSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            follower = Followers(**serializer.validated_data)
            follower.user_id = user_id
            follower.save()
            response_data.update({"message": "successfully followed"})
            return Response(data=response_data, status=status.HTTP_200_OK)
        response_data = {"message": "already followed"}
        return Response(data=response_data, status=status.HTTP_200_OK)

    @staticmethod
    def unfollow(request, *args, **kwargs):
        if Followers.objects.filter(page_id=kwargs["pk"]).exists():
            Followers.objects.filter(page_id=kwargs["pk"]).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def feed(request, *args, **kwargs):
        followed = Followers.objects.filter(user_id=request.user.user_id).values_list(
            "page_id", flat=True
        )
        posts = Post.objects.filter(page__id__in=followed).order_by("-created_at")
        serializer = PostSerializer(posts, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def block(self, request, *args, **kwargs):
        page = self.get_object()
        unblock_date = request.data.get("unblock_date", None)

        if not page.is_blocked and unblock_date:
            page.is_blocked = True
            page.unblock_date = unblock_date
            page.save()
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "incorrect unblock_date passed"},
            )
        serializer = PageDetailSerializer(page)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by("name")
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def list(self, request, *args, **kwargs):
        page = request.query_params.get("page", 1)
        limit = request.query_params.get("limit", 30)
        filter_by_name = request.query_params.get("filter_by_name", "")
        params_serializer = PaginationAndFiltersSerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        query_set = Tag.objects.filter(name__icontains=filter_by_name)
        paginator = Paginator(query_set, limit)
        items = paginator.page(page).object_list
        serializer = TagSerializer(items, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_permissions(self):
        if self.action == "create_post":
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [IsAdminModerCreatorOrReadOnly]
        return [permission() for permission in self.permission_classes]
