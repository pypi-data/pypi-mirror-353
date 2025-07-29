try:
    from ._version import __version__
except ImportError:
    __version__ = 'unknown'
from .main import stistarg, findcheckbox, calculate_flux_centroid, \
                  display_results, parse
