"""
This module contains functions for resetting view states in the TRCViewer application.
These functions were extracted from the main class to improve code organization.
"""

## AUTHORSHIP INFORMATION
__author__ = "HunMin Kim"
__copyright__ = ""
__credits__ = [""]
__license__ = ""
# from importlib.metadata import version
# __version__ = version('MStudio')
__maintainer__ = "HunMin Kim"
__email__ = "hunminkim98@gmail.com"
__status__ = "Development"

import logging

logger = logging.getLogger(__name__)

def reset_main_view(self):
    """
    Resets the main 3D OpenGL view to its default state based on data limits.
    """
    # Check if the OpenGL renderer exists
    if hasattr(self, 'gl_renderer') and self.gl_renderer:
        # Check if the renderer has the reset_view method and call it
        if hasattr(self.gl_renderer, 'reset_view'):
            try:
                self.gl_renderer.reset_view()
            except Exception as e:
                logger.error("Error calling gl_renderer.reset_view: %s", e, exc_info=True)
        else:
            logger.warning("OpenGL renderer does not have a 'reset_view' method.")
    else:
        logger.warning("OpenGL renderer not found, cannot reset view.")

def reset_graph_view(self):
    """
    Resets the marker graph view to its initial limits.
    """
    if hasattr(self, 'marker_axes') and hasattr(self, 'initial_graph_limits'):
        for ax, limits in zip(self.marker_axes, self.initial_graph_limits):
            ax.set_xlim(limits['x'])
            ax.set_ylim(limits['y'])
        if hasattr(self, 'marker_canvas') and hasattr(self.marker_canvas, 'draw'):
            self.marker_canvas.draw()
