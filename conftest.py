from django.conf import settings


def pytest_configure():
    # Dynamically configure the Django settings with the minimum necessary to
    # get Django running tests.
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.admin',
            'django.contrib.sessions',
            'tests.testapp',
            'django_extensions',
        ],
        MIDDLEWARE_CLASSES=(
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        # Django replaces this, but it still wants it. *shrugs*
        DATABASE_ENGINE='django.db.backends.sqlite3',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        MEDIA_ROOT='/tmp/django_extensions_test_media/',
        MEDIA_PATH='/media/',
        ROOT_URLCONF='tests.urls',
        DEBUG=True,
        TEMPLATE_DEBUG=True,
    )
