#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from traits.api import Any, Float
from enable.tools.api import AttributeDragTool

class PlotDragTool(AttributeDragTool):
    """ Drag tool that selects a plot
    
    This is a standard attribute drag tool that in addition is activated only
    when the mouse click satisfies the hittest of a plot, and highlights the
    plot when dragging by changing its alpha.
    
    """
  
    # XXX this has many hard-coded things - it should probably be made general
    # and put into Chaco or Enable
  
    #: the plot we are targeting - this can be anything which implements a
    #: hittest() method
    plot = Any
    
    #: the amount to multiply the alpha of the plot by when dragging
    alpha_multiple = Float(1.25)
    
    #: internal store of plot's original alpha value while dragging
    _old_alpha = Float
    
    def is_draggable(self, x, y):
        return self.plot.hittest((x, y))
    
    def _drag_button_down(self, event):
        consume = super(PlotDragTool, self)._drag_button_down(event)
        if consume and self.alpha_multiple != 1.0 and hasattr(self.plot, 'alpha'):
            self._old_alpha = self.plot.alpha
            self.plot.alpha = min(self.plot.alpha*self.alpha_multiple, 1.0)
        return consume
    
    def drag_end(self, event):
        super(PlotDragTool, self).drag_end(event)
        if self.alpha_multiple != 1.0 and hasattr(self.plot, 'alpha'):
            self.plot.alpha = self._old_alpha

