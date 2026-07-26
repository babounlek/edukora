"""
URL configuration for edtech_cm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from catalog.sitemap import sitemap_chunk, sitemap_index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("users.urls")),
    path("catalog/", include("catalog.urls")),
    path("subscriptions/", include("subscriptions.urls")),
    path("payments/", include("payments.urls")),
    path("access/", include("access.urls")),
    path("quiz/", include("quiz.urls")),
    path("sitemap.xml", sitemap_index, name="sitemap-index"),
    path("sitemap-<int:page>.xml", sitemap_chunk, name="sitemap-chunk"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
