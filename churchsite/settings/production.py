from .base import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
# import string,random; uni=string.ascii_letters+string.digits+string.punctuation; print repr(''.join([random.SystemRandom().choice(uni) for i in range(random.randint(45,50))]))

SECRET_KEY = os.environ.get('SECRET_KEY')


INSTALLED_APPS += (
    )

ALLOWED_HOSTS = [ 'amayzing-dnow.herokuapp.com']

DATABASES['default'] = dj_database_url.config()
