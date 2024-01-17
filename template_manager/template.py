from .document_part import DocumentPart
from .inner_environment import InnerEnvironment
from .wobject import Wobject
from .outer_environment import OuterEnvironment


class Template:
    def __init__(self, name, version_code, version_name, description, implicit_outer_environment,
                 document_parts=None, wobjects=None, outer_environments=None, inner_environments=None):
        self.name = name
        self.version_code = version_code
        self.version_name = version_name
        self.description = description
        self.implicit_outer_environment = implicit_outer_environment

        self.document_parts = [DocumentPart(**dp) for dp in (document_parts or [])]

        self.wobjects = [Wobject(**ob) for ob in (wobjects or [])]

        self.classic_outer_environments = [OuterEnvironment(**oe) for oe in outer_environments.get("classic", [])]
        self.fragile_outer_environments = [OuterEnvironment(**oe) for oe in outer_environments.get("fragile", [])]

        self.classic_inner_environemnts = [InnerEnvironment(**ie) for ie in inner_environments.get("classic", [])]
        self.short_inner_environemnts = [InnerEnvironment(**ie) for ie in inner_environments.get("short", [])]

