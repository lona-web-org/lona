from lona.routing import Route

routes = [
    Route('/foo', 'views.py::foo'),
    Route('/bar', 'views.py::bar'),
    Route('/form', 'views.py::form_view'),
    Route('/grid', 'views.py::grid_view'),
    Route('/sort', 'views.py::sort'),
]
