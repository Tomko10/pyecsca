"""Package for communicating with targets of measurement."""

from .ISO7816 import *
from .base import *

has_chipwhisperer = False
has_pyscard = False

try:
    import chipwhisperer

    has_chipwhisperer = True
except ImportError:
    pass

try:
    import pyscard

    has_pyscard = True
except ImportError:
    pass

if has_pyscard:
    from .PCSC import *

if has_chipwhisperer:
    from .chipwhisperer import *