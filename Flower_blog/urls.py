"""Flower_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


# 存放映射关系
urlpatterns = [  # 定位APPS
    path('admin/', admin.site.urls),

    path('article/', include('article.urls', namespace='article')),  # article/ 分配app访问路径，include将路径分发给下一步处理，namespace保证反查到唯一url

    path('userprofile/', include('userprofile.urls', namespace='userprofile')),

    path('identify/', include('identify.urls', namespace='identify')),

    path('comment/', include('comment.urls', namespace='comment')),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)