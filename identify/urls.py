from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'identify'  # Django2.0之后，app的urls.py必须配置app_name，否则会报错。

urlpatterns = [
    path('identify_flower/', views.upload_view, name='upload_view'),
]
