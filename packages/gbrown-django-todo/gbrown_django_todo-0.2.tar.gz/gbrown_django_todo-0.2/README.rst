============
django-todo
============

django-polls is a Django app to help users keep track of their TODO items.
Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "todo" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "django_todo",
    ]

2. Include the polls URLconf in your project urls.py like this::

    path("todos/", include("django_todo.urls")),

3. Run ``python manage.py migrate`` to create the models.

4. Start the development server and visit the admin to create a todo.

5. Visit the ``/todos/`` URL to create and view todos.