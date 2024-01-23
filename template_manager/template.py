from .document_part import DocumentPart
from .inner_environment import InnerEnvironment
from .shorthand import Shorthand
from .wobject import Wobject
from .outer_environment import OuterEnvironment


class Template:
    def __init__(self, name, version_code, version_name, description, implicit_outer_environment,
                 document_parts=None, wobjects=None, outer_environments=None, inner_environments=None,
                 shorthands=None):
        self.name = name
        self.version_code = version_code
        self.version_name = version_name
        self.description = description
        self.implicit_outer_environment = implicit_outer_environment

        self.document_parts = [DocumentPart(**dp) for dp in (document_parts or [])]

        self.wobjects = [Wobject(**ob) for ob in (wobjects or [])]

        self.classic_outer_environments = [OuterEnvironment(**oe) for oe in outer_environments.get("classic", [])]
        self.fragile_outer_environments = [OuterEnvironment(**oe) for oe in outer_environments.get("fragile", [])]

        self.inner_environments = [InnerEnvironment(**ie) for ie in (inner_environments or [])]

        self.shorthand_hash = Shorthand(**shorthands.get("hash"), type="#")
        self.shorthand_at = Shorthand(**shorthands.get("at"), type="@")

