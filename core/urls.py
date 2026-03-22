from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'core'

urlpatterns = [
    path('',           views.redirect_to_dashboard),
    path('dashboard/', views.dashboard,        name='dashboard'),
    path('people/',    views.people_list,      name='people_list'),
    path('units/',     views.units_list,       name='units_list'),
    path('courses/',   views.courses_list,     name='courses_list'),
    path('programs/',  views.programs_list,    name='programs_list'),
    path('grants/',    views.grants_list,      name='grants_list'),
    path('research/',  views.research_list,    name='research_list'),
    path('import/',    views.import_data,      name='import_data'),
    path('import/run/', views.run_import,      name='run_import'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)