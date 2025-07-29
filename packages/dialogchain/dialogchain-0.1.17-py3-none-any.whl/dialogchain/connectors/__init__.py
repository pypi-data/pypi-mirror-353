"""Connectors for DialogChain data sources and destinations."""

from .base import Source, Destination
from .sources.rtsp import RTSPSource
from .sources.imap import IMAPSource
from .sources.file import FileSource
from .sources.timer import TimerSource
from .destinations.http import HTTPDestination
from .destinations.email import EmailDestination
from .destinations.file import FileDestination
from .destinations.log import LogDestination

# Re-export for backward compatibility
__all__ = [
    'Source',
    'Destination',
    'RTSPSource',
    'IMAPSource',
    'FileSource',
    'TimerSource',
    'HTTPDestination',
    'EmailDestination',
    'FileDestination',
    'LogDestination',
]
