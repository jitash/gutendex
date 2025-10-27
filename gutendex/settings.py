import os
import environ
import dj_database_url

# 初始化环境
env = environ.Env()
environ.Env.read_env()

# 数据库配置
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

# 静态文件路径
STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', default='/app/staticfiles')

# 媒体文件路径
MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default='/app/media')

# 邮件配置（可选）
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
