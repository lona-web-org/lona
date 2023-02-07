from lona.html.data_binding.select2 import Select2, Option2
from lona.html.data_binding.inputs import *  # NOQA: F403
from lona.html.data_binding.select import Select, Option
from lona.html.parsing import _setup_node_classes_cache
from lona.events.event_types import *  # NOQA: F403
from lona.html.widgets import HTML as HTML1
from lona.html.parsing import HTML as HTML2
from lona.html.nodes import *  # NOQA: F403
from lona.compat import get_client_version
from lona.html.widget import Widget

_setup_node_classes_cache()


def HTML(*args, **kwargs):
    if get_client_version() == 1:
        return HTML1(*args, **kwargs)

    return HTML2(*args, **kwargs)
