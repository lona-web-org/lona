from lona.html.nodes.inline_text_semantics import *  # NOQA: F403
from lona.html.nodes.image_and_multimedia import *  # NOQA: F403
from lona.html.nodes.content_sectioning import *  # NOQA: F403
from lona.html.nodes.document_metadata import *  # NOQA: F403
from lona.html.nodes.embedded_content import *  # NOQA: F403
from lona.html.nodes.sectioning_root import *  # NOQA: F403
from lona.html.nodes.forms.select2 import Select2, Option2
from lona.html.nodes.table_content import *  # NOQA: F403
from lona.html.nodes.text_content import *  # NOQA: F403
from lona.html.nodes.forms.inputs import *  # NOQA: F403
from lona.html.parsing import _setup_node_classes_cache
from lona.html.nodes.forms.select import Select, Option
from lona.html.nodes.scripting import *  # NOQA: F403
from lona.events.event_types import *  # NOQA: F403
from lona.html.nodes.forms import *  # NOQA: F403
from lona.html.widgets import HTML as HTML1
from lona.html.parsing import HTML as HTML2
from lona.compat import get_client_version
from lona.html.widget import Widget

_setup_node_classes_cache()


def HTML(*args, **kwargs):
    if get_client_version() == 1:
        return HTML1(*args, **kwargs)

    return HTML2(*args, **kwargs)
