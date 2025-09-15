from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
# from api.views import EmployeViewSet, PresenceViewSet, RapportViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny


# router par défaut 
router = routers.DefaultRouter()

# On enregistre nos ViewSets dans le router
# router.register(r'employes', EmployeViewSet, basename='employe')
# router.register(r'presences', PresenceViewSet, basename='presence')
# router.register(r'rapports', RapportViewSet, basename='rapport')

# On configure la vue Swagger (copier depui doc swagger)
schema_view = get_schema_view(
    openapi.Info(
        title="API Suivi Employés",          
        default_version='v1',                
        description="Notre  AAPI pour gérer, employés, présences, et rapports",  
    ),
    public=True,
    permission_classes=(AllowAny,),           
)

# On définit la liste des URL disponibles dans notre projet Django.
urlpatterns = [
    path('admin/', admin.site.urls),  
    path("api/", include("api.urls")),
    path('api/users/', include('users.urls')),  
    path('api/', include(router.urls)),

    # Swagger / Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
# from api.views import EmployeViewSet, PresenceViewSet, RapportViewSet
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny


# router par défaut 
router = routers.DefaultRouter()

# On enregistre nos ViewSets dans le router
# router.register(r'employes', EmployeViewSet, basename='employe')
# router.register(r'presences', PresenceViewSet, basename='presence')
# router.register(r'rapports', RapportViewSet, basename='rapport')

# On configure la vue Swagger (copier depui doc swagger)
schema_view = get_schema_view(
    openapi.Info(
        title="API Suivi Employés",          
        default_version='v1',                
        description="Notre  AAPI pour gérer, employés, présences, et rapports",  
    ),
    public=True,
    permission_classes=(AllowAny,),           
)

# On définit la liste des URL disponibles dans notre projet Django.
urlpatterns = [
    path('admin/', admin.site.urls),  
    path("api/", include("api.urls")),
    path('api/users/', include('users.urls')),  
    path('api/', include(router.urls)),

    # Swagger / Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]



