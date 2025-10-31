import os
import environ
import dj_database_url

# 初始化环境
env = environ.Env()
environ.Env.read_env()

# 安全密钥
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')

# 调试模式
DEBUG = env.bool('DEBUG', default=False)

# 允许的主机
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# 应用配置
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # 静态文件支持，必需 for collectstatic
    'corsheaders',
    'rest_framework',
    'books',
]

# 中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL 配置
ROOT_URLCONF = 'gutendex.urls'

# 模板配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gutendex', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI 应用
WSGI_APPLICATION = 'gutendex.wsgi.application'

# 数据库配置
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 国际化
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 静态文件路径
STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', default='/app/staticfiles')

# 媒体文件路径
MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default='/app/media')

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS 配置
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework 配置
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 32
}

# 邮件配置（可选）
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_HOST_ADDRESS = env('EMAIL_HOST_ADDRESS', default='')

# 管理员邮箱（用于发送同步日志）
ADMIN_EMAILS = env.list('ADMIN_EMAILS', default=[])

# 数据同步目录配置
CATALOG_TEMP_DIR = env('CATALOG_TEMP_DIR', default='/tmp/gutendex-catalog-temp')
CATALOG_RDF_DIR = env('CATALOG_RDF_DIR', default='/app/catalog')
CATALOG_LOG_DIR = env('CATALOG_LOG_DIR', default='/app/logs')

# 数据同步 API 令牌（用于通过 HTTP 触发同步）
SYNC_SECRET_TOKEN = env('SYNC_SECRET_TOKEN', default='')
