from rest_framework import serializers

from blog.models import Post, Tag, Page, Followers, Likes


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class FeedPostSerializer(serializers.ModelSerializer):
    page_title = serializers.CharField(source='page.name')
    likes = serializers.IntegerField(source='likes.count')
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'created_at',
            'updated_at',
            'content',
            'page_title',
            'reply_to',
            'page',
            'likes',
            'has_liked',
        ]

    def get_has_liked(self, obj):
        user = self.context['request'].custom_user
        return Likes.objects.filter(user_id=user.user_id).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'


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
        fields = ['user_id']


class FollowerSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(required=False)

    class Meta:
        model = Followers
        fields = '__all__'
