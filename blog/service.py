from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from InnoterService.settings import logger
from blog.models import Page, Followers, Post, Tag, Likes
from blog.serializers import (
    PaginationParamsSerializer,
    PageDetailSerializer,
    FollowerResponseSerializer,
    FollowerSerializer,
    PostSerializer,
    PaginationAndFiltersSerializer,
    TagSerializer,
)


def page_detail(page: Page, request: Request) -> Response:
    if not page.is_blocked:
        page_number = request.query_params.get('page', 1)
        limit = request.query_params.get('limit', 30)
        params_serializer = PaginationParamsSerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        posts = page.posts.all()
        paginator = Paginator(posts, limit)
        items = paginator.page(page_number).object_list
        serializer = PageDetailSerializer(page)
        serializer.posts = items
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    else:
        logger.error(f'Request to retrieve blocked page with pk={page.id}')
        return Response(
            data={'message': 'Oops, page is blocked!'},
            status=status.HTTP_404_NOT_FOUND,
        )


def get_followers(page: Page) -> Response:
    followers = Followers.objects.filter(page_id=page.id)
    serializer = FollowerResponseSerializer(followers, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


def follow_to_page(request: Request, pk: str) -> Response:
    if not Followers.objects.filter(page=pk).exists():
        user_id = request.user.user_id
        response_data = {}
        data = {'page': pk}
        serializer = FollowerSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        follower = Followers(**serializer.validated_data)
        follower.user_id = user_id
        follower.save()
        response_data.update({'message': 'successfully followed'})
        return Response(data=response_data, status=status.HTTP_200_OK)
    response_data = {'message': 'already followed'}
    return Response(data=response_data, status=status.HTTP_200_OK)


def unfollow(pk: str) -> Response:
    if Followers.objects.filter(page_id=pk).exists():
        Followers.objects.filter(page_id=pk).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def list_feed(request: Request) -> Response:
    followed = Followers.objects.filter(user_id=request.user.user_id).values_list(
        'page_id', flat=True
    )
    posts = Post.objects.filter(page__id__in=followed).order_by('-created_at')
    serializer = PostSerializer(posts, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


def block_page(page: Page, unblock_date: str) -> Response:
    if not page.is_blocked and unblock_date:
        page.is_blocked = True
        page.unblock_date = unblock_date
        page.save()
    else:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'message': 'incorrect unblock_date passed'},
        )
    serializer = PageDetailSerializer(page)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


def list_tags_with_filtering(
    request: Request, page: int, limit: int, filter_by_name: str
) -> Response:
    params_serializer = PaginationAndFiltersSerializer(data=request.query_params)
    params_serializer.is_valid(raise_exception=True)
    query_set = Tag.objects.filter(name__icontains=filter_by_name)
    paginator = Paginator(query_set, limit)
    items = paginator.page(page).object_list
    serializer = TagSerializer(items, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


def like_post(post: Post, user_id: str) -> Response:
    if not Likes.objects.filter(user_id=user_id).exists():
        like = Likes(user_id=user_id, post=post)
        like.save()
        return Response(
            status=status.HTTP_201_CREATED, data={'message': 'successfully liked'}
        )
    else:
        like = Likes.objects.get(user_id=user_id, post=post)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
