from types import MethodType

from django.contrib import admin


admin.site.site_header = "Yuki Blog Console"
admin.site.site_title = "Yuki Blog"
admin.site.index_title = "欢迎回来"
admin.site.index_template = "admin/index.html"


APP_ORDER = {
    "blog": 10,
    "core": 20,
}

MODEL_ORDER = {
    "blog": {
        "Post": 10,
        "Note": 20,
        "NoteCollection": 30,
        "Thought": 40,
        "Memory": 50,
        "Category": 60,
        "Tag": 70,
    },
    "core": {
        "Project": 10,
        "Quote": 20,
    },
}


_original_get_app_list = admin.site.get_app_list


def get_app_list(self, request, app_label=None):
    app_list = _original_get_app_list(
        request,
        app_label,
    )

    app_list = [
        app
        for app in app_list
        if app["app_label"] != "auth"
    ]

    app_list.sort(
        key=lambda app: APP_ORDER.get(
            app["app_label"],
            999,
        )
    )

    for app in app_list:
        model_order = MODEL_ORDER.get(
            app["app_label"],
            {},
        )

        app["models"].sort(
            key=lambda model: model_order.get(
                model["object_name"],
                999,
            )
        )

    return app_list


admin.site.get_app_list = MethodType(
    get_app_list,
    admin.site,
)
