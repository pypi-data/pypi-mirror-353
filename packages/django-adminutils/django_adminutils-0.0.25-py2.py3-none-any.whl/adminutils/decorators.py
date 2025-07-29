import functools

from django.template.loader import render_to_string


def options(**kwargs):
    map = {
        "desc": "short_description",
        "order": "admin_order_field",
    }

    def wrapper(func):
        for k, v in kwargs.items():
            setattr(func, map.get(k, k), v)
        return func

    return wrapper


def rendered_field(template):
    def processor(func):
        @functools.wraps(func)
        def renderer(self, obj):
            context = func(self, obj)
            return render_to_string(template, context)

        return renderer

    return processor
