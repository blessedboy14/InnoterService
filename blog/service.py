from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

import boto3

from InnoterService import settings
from InnoterService.settings import logger
from blog.models import Page, Followers, Post, Tag, Likes
from blog.serializers import (
    PaginationParamsSerializer,
    PageDetailSerializer,
    FollowerResponseSerializer,
    FollowerSerializer,
    PaginationAndFiltersSerializer,
    TagSerializer,
    FeedPostSerializer,
    PageNamesSerializer,
    PageSerializer,
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
        context = {'request': request}
        serializer = PageDetailSerializer(page, context=context)
        serializer.posts = items
        output = {**serializer.data, 'total_pages': paginator.num_pages}
        return Response(data=output, status=status.HTTP_200_OK)
    else:
        logger.error(f'Request to retrieve blocked page with pk={page.id}')
        return Response(
            data='Oops, page is blocked!',
            status=status.HTTP_404_NOT_FOUND,
        )


def get_followers(page: Page) -> Response:
    followers = Followers.objects.filter(page_id=page.id)
    serializer = FollowerResponseSerializer(followers, many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


def update_page_data(
    request: Request, image: InMemoryUploadedFile, parent_partial_update
) -> Response:
    result, filename = _upload_image_to_s3(image, request.custom_user.user_id)
    if result:
        request.data['image_url'] = filename
        return parent_partial_update(request)
    else:
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data="Can't save image to s3"
        )


def _upload_image_to_s3(image: InMemoryUploadedFile, user_id: str) -> tuple[bool, str]:
    s3 = boto3.client(
        's3',
        endpoint_url=f'http://{settings.LOCALSTACK_HOST}:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
    )
    try:
        filename = f'page-images/{user_id}/{image.name}'
        s3.upload_fileobj(image, 'images-storage', filename)
        return True, filename
    except Exception:
        return False, ''


def create_page_with_image(
    request: Request, serializer: PageSerializer, image: InMemoryUploadedFile
) -> Response:
    if image:
        result, filename = _upload_image_to_s3(image, request.custom_user.user_id)
        if result:
            serializer.save(user_id=request.custom_user.user_id, image_url=filename)
        else:
            serializer.save(
                user_id=request.custom_user.user_id, image_url='https://example.com'
            )
    else:
        serializer.save(
            user_id=request.custom_user.user_id, image_url='https://example.com'
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def follow_to_page(request: Request, pk: str) -> Response:
    if not Followers.objects.filter(
        page=pk, user_id=request.custom_user.user_id
    ).exists():
        user_id = request.custom_user.user_id
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


def unfollow(pk: str, request: Request) -> Response:
    if Followers.objects.filter(
        page_id=pk, user_id=request.custom_user.user_id
    ).exists():
        Followers.objects.filter(
            page_id=pk, user_id=request.custom_user.user_id
        ).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def list_users_pages(user_id: str) -> Response:
    pages = Page.objects.filter(user_id=user_id)
    serializer = PageNamesSerializer(pages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def list_feed(request: Request) -> Response:
    followed = Followers.objects.filter(
        user_id=request.custom_user.user_id
    ).values_list('page_id', flat=True)
    posts = Post.objects.filter(page__id__in=followed, page__is_blocked=False).order_by(
        '-created_at'
    )
    context = {'request': request}
    serializer = FeedPostSerializer(posts, many=True, context=context)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


def block_page(page: Page, unblock_date: str, request: Request) -> Response:
    if not page.is_blocked and unblock_date:
        page.is_blocked = True
        page.unblock_date = unblock_date
        page.save()
    else:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'message': 'incorrect unblock_date passed'},
        )

    serializer = PageDetailSerializer(page, context={'request': request})
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
    output = {'tags': serializer.data, 'total_tags': paginator.num_pages}
    return Response(data=output, status=status.HTTP_200_OK)


def like_post(post: Post, user_id: str) -> Response:
    if not Likes.objects.filter(user_id=user_id, post=post).exists():
        like = Likes(user_id=user_id, post=post)
        like.save()
        return Response(
            status=status.HTTP_201_CREATED,
            data={
                'message': 'successfully liked',
                'likes': Likes.objects.filter(post=post).count(),
            },
        )
    else:
        like = Likes.objects.get(user_id=user_id, post=post)
        like.delete()
        return Response(
            status=status.HTTP_200_OK,
            data={'likes': Likes.objects.filter(post=post).count()},
        )
