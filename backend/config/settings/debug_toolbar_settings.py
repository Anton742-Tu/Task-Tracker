def show_toolbar(request):
    """
    Показывать toolbar только для определенных путей
    """
    # Исключаем админку и API
    excluded_paths = ["/admin/", "/api/", "/swagger/", "/redoc/"]
    if any(request.path.startswith(path) for path in excluded_paths):
        return False
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    "RENDER_PANELS": True,
    "RESULTS_STORE_SIZE": 25,
}
