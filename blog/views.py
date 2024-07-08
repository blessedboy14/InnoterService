from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from InnoterService import settings
from blog.models import Post, Page, Tag
from blog.permissions import (
    IsAdminModerCreatorOrReadOnly,
    IsCreator,
    IsAdminOrGroupModerator,
    IsAuthenticated,
)
from blog.serializers import (
    PostSerializer,
    PageSerializer,
    TagSerializer,
)
from blog.service import (
    page_detail,
    get_followers,
    follow_to_page,
    unfollow,
    list_feed,
    block_page,
    list_tags_with_filtering,
    like_post,
    list_users_pages,
    create_page_with_image,
    update_page_data,
)

logger = settings.logger


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all().order_by('-created_at')
    serializer_class = PageSerializer
    permission_classes = [IsAdminModerCreatorOrReadOnly]
    save_actions = ('create_page', 'retrieve', 'follow', 'unfollow')
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_permissions(self):
        if (
            self.action in self.save_actions
            or self.action == 'feed'
            or self.action == 'perform_create'
        ):
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'partial_update':
            self.permission_classes = [IsCreator]
        elif self.action == 'block':
            self.permission_classes = [IsAdminOrGroupModerator]
        elif self.action == 'get_users_pages':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminModerCreatorOrReadOnly]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        image = self.request.FILES.get('image')
        return create_page_with_image(self.request, serializer, image)

    def partial_update(self, request, *args, **kwargs):
        image = self.request.FILES.get('image')
        if image:
            return update_page_data(request, image, super().partial_update)
        else:
            return super().partial_update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        page = self.get_object()
        return page_detail(page, request)

    def retrieve_followers(self, request, *args, **kwargs):
        page = self.get_object()
        return get_followers(page)

    @staticmethod
    def follow(request, *args, **kwargs):
        return follow_to_page(request, kwargs['pk'])

    @staticmethod
    def unfollow(request, *args, **kwargs):
        return unfollow(kwargs['pk'], request)

    @staticmethod
    def feed(request, *args, **kwargs):
        return list_feed(request)

    @staticmethod
    def get_users_pages(request, *args, **kwargs):
        user_id = kwargs['pk']
        return list_users_pages(user_id)

    def block(self, request, *args, **kwargs):
        page = self.get_object()
        unblock_date = request.data.get('unblock_date', None)
        return block_page(page, unblock_date, request)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        page = request.query_params.get('page', 1)
        limit = request.query_params.get('limit', 30)
        filter_by_name = request.query_params.get('filter_by_name', '')
        return list_tags_with_filtering(request, page, limit, filter_by_name)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create_post' or self.action == 'like':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminModerCreatorOrReadOnly]
        return [permission() for permission in self.permission_classes]

    def like(self, request, *args, **kwargs):
        post = self.get_object()
        user_id = request.custom_user.user_id
        return like_post(post, user_id)
