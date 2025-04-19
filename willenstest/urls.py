from django.contrib import admin
from django.urls import path, include
from .views import quiz_view, results_view, upload_csv_view

urlpatterns = [
    path('', quiz_view, name='quiz'),
    path('results/', results_view, name='results'),
    path('upload/', upload_csv_view, name='upload_csv'),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]