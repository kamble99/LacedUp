# A context processor in Django is a Python function that takes a request object as input and returns a dictionary that gets added to the template context.
# This allows you to make certain data available globally across all templates without having to explicitly pass them in every view


from category.models import Category
def menu_links(request):
    links=Category.objects.all()
    return dict(links=links)
