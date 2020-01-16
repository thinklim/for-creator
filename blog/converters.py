from django.urls.converters import StringConverter


class BlogPostSlugConverter(StringConverter):
    regex = '[-\w]+'