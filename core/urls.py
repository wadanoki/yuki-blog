from django.urls import path

from . import views


app_name = "core"


urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "projects/",
        views.project_list,
        name="project_list",
    ),

    path(
        "quotes/",
        views.quote_list,
        name="quote_list",
    ),

    path(
        "pages/<slug:page_slug>/",
        views.site_page,
        name="site_page",
    ),
]
