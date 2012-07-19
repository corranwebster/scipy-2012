#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#


from traits.api import Float, Enum, Bool, Str, Any
from enable.api import ColorTrait, LineStyle
from enable.tools.value_drag_tool import identity_mapper
from chaco.api import AbstractOverlay


class LineOverlay(AbstractOverlay):
    """ Abstract base class that draws a line at a location in data space
    
    Subclasses must override the get_value() method.  This class should supply
    either an x_mapper or y_mapper depending on orientation which has to provide
    map_screen() method that maps from data space to screen space.
    
    """
    
    # This tool is visible (overrides BaseTool).
    visible = True
    
    # This tool is drawn as an overlay (overrides BaseTool).
    draw_mode = "overlay"
    
    orientation = Enum(['horizontal','vertical'])
    
    #: mapper that maps from horizontal screen coordinate to data coordinate
    x_mapper = Any
    
    #: mapper that maps from vertical screen coordinate to data coordinate
    y_mapper = Any

    # TODO:STYLE

    # Color of the line.
    line_color = ColorTrait("lightgrey")
    
    # Width in pixels of the line.
    line_width = Float(1.0)
    
    # Dash style of the line.
    line_style = LineStyle("solid")
    
    # should we draw a thumb?
    thumb = Bool(True)
    
    thumb_color = ColorTrait("lightgrey")
    
    thumb_size = 3
    
    def get_value(self):
        """ Return the current value that is being modified
        
        """
        pass
    
    def overlay(self, other_component, gc, view_bounds=None, mode="normal"):
        x_value, y_value = self.get_value()
        
        if self.orientation == 'horizontal':
            sy = self.y_mapper.map_screen(y_value)
            self._draw_horizontal_line(gc, sy)
        else:
            sx = self.x_mapper.map_screen(x_value)
            self._draw_vertical_line(gc, sx)
    
    def hittest(self, screen_pt, threshold=7.0):
        x, y = screen_pt
        x_value, y_value = self.get_value()
        
        if self.orientation == 'horizontal':
            sy = self.y_mapper.map_screen(y_value)
            return abs(y-sy) <= threshold
        else:
            sx = self.x_mapper.map_screen(x_value)
            return abs(x-sx) <= threshold
        return False

    # traits default handlers

    def _x_mapper_default(self):
        # if the component has an x_mapper, try to sue it by default
        return getattr(self.component, 'x_mapper', identity_mapper)

    def _y_mapper_default(self):
        # if the component has an x_mapper, try to sue it by default
        return getattr(self.component, 'y_mapper', identity_mapper)


    def _draw_vertical_line(self, gc, sx):
        """ Draws a vertical line through screen point (sx,sy) having the height
        of the tool's component.
        
        """
        if sx < self.component.x or sx > self.component.x2:
            return

        with gc:
            gc.clip_to_rect(self.component.x, self.component.y,
                self.component.width, self.component.height)
            gc.set_stroke_color(self.line_color_)
            gc.set_line_width(self.line_width)
            gc.set_line_dash(self.line_style_)
            gc.move_to(sx, self.component.y)
            gc.line_to(sx, self.component.y2)
            gc.stroke_path()
            if self.thumb:
                gc.set_fill_color(self.thumb_color_)
                bottom = (self.component.y+self.component.y2)/2.-self.thumb_size
                left = sx-self.thumb_size
                gc.draw_rect((left, bottom, 2*self.thumb_size, 2*self.thumb_size))
                
        return

    def _draw_horizontal_line(self, gc, sy):
        """ Draws a horizontal line through screen point (sx,sy) having the
        width of the tool's component.
        
        """
        if sy < self.component.y or sy > self.component.y2:
            return

        with gc:
            gc.clip_to_rect(self.component.x, self.component.y,
                self.component.width, self.component.height)
            gc.set_stroke_color(self.line_color_)
            gc.set_line_width(self.line_width)
            gc.set_line_dash(self.line_style_)
            gc.move_to(self.component.x, sy)
            gc.line_to(self.component.x2, sy)
            gc.stroke_path()
            if self.thumb:
                gc.set_fill_color(self.thumb_color_)
                left = (self.component.x+self.component.x2)/2.-self.thumb_size
                bottom = sy-self.thumb_size
                gc.draw_rect((left, bottom, 2*self.thumb_size, 2*self.thumb_size))
        return


class AttributeLineOverlay(LineOverlay):
    """  Class which draws a line at a data space point specified by an attribute
    
    """
        
    #: the model object which has the attributes we are modifying
    model = Any
    
    #: the name of the attributes that is modified by horizontal motion
    x_attr = Str
    
    #: the name of the attributes that is modified by vertical motion
    y_attr = Str

   
    def get_value(self):
        """ Get the current value of the attributes
        
        Returns a 2-tuple of (x, y) values.  If either x_attr or y_attr is
        the empty string, then the corresponding component of the tuple is
        None.
        
        """
        x_value = None
        y_value = None
        if self.x_attr:
            x_value = getattr(self.model, self.x_attr)
        if self.y_attr:
            y_value = getattr(self.model, self.y_attr)
        return (x_value, y_value)

