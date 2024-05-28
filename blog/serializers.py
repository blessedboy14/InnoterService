from rest_framework import serializers

from blog.models import Post, Tag, Page, Followers


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"


class PageDetailSerializer(PageSerializer):
    tags = TagSerializer(many=True, read_only=True)
    posts = PostSerializer(many=True, read_only=True)


class PaginationParamsSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1, required=False)
    limit = serializers.IntegerField(min_value=1, max_value=150, required=False)


class PaginationAndFiltersSerializer(PaginationParamsSerializer):
    filter_by_name = serializers.CharField(required=False)


class FollowerResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Followers
        fields = ["user_id"]


class FollowerSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(required=False)

    class Meta:
        model = Followers
        fields = "__all__"
