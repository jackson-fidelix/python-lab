from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def root_redirect(request):
    return redirect('/chat/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chat_app.urls')),
    path('', root_redirect),
]