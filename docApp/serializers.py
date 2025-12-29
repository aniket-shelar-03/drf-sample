from rest_framework import serializers
from .models import Book, Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        read_only=False,
        queryset=Author.objects.all(),
        help_text="Foreign key reference - Author(Author.id)"
    )

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'num_pages', 'published']