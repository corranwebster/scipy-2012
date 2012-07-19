#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

import numpy as np
from skimage.data import moon

from traits.api import HasTraits, Float, Array, Callable, Instance, Property, cached_property
from traitsui.api import View, HSplit, VGroup, Item, RangeEditor, InstanceEditor
from enable.api import ComponentEditor
from enable.tools.api import AttributeDragTool
from chaco.api import ArrayPlotData, Plot, TransformColorMapper, gray
from chaco.overlays.api import SimpleInspectorOverlay, basic_formatter

from plot_drag_tool import PlotDragTool
from histogram_overlays import AttributeLineOverlay

class UnitMap(HasTraits):
    """ A function of the form (m*x+b)**gamma
    
    """

    low = Float(0.0)

    high = Float(1.0)

    slope = Float(1.0)
    
    intercept = Float(0.0)
    
    gamma = Float(1.0)
    
    function = Property(Callable, depends_on=['low', 'high', 'slope',
        'intercept', 'gamma'])
    
    @cached_property
    def _get_function(self):
        return lambda x: np.clip((self.slope*np.clip(x, self.low, self.high)
                + self.intercept), 0., 1.)**self.gamma
    

class HistogramView(HasTraits):
    
    unit_map = Instance(UnitMap)
    
    image_data = Array
    
    image_histogram = Property(Array, depends_on='image_data')
    
    mapped_histogram = Property(Array, depends_on=['image_data', 'unit_map.function'])

    plot_data = Instance(ArrayPlotData)
    
    plot = Instance(Plot)
    
    @cached_property
    def _get_image_histogram(self):
        return np.histogram(self.image_data/256., bins=256, range=(0.0, 1.0))[0]
    
    @cached_property
    def _get_mapped_histogram(self):
        if self.unit_map is not None:
            return np.histogram(self.unit_map.function(self.image_data/256.), bins=256,
                range=(0.0, 1.0))[0]
        else:
            return np.zeros(shape=(256,))
    
    def _plot_data_default(self):
        x = np.arange(256.)/256
        return ArrayPlotData(
            image_histogram=self.image_histogram,
            mapped_histogram=self.mapped_histogram,
            x=x
        )
    
    def _image_histogram_changed(self):
        self.plot_data.set_data('image_histogram', self.image_histogram)
    
    def _mapped_histogram_changed(self):
        self.plot_data.set_data('mapped_histogram', self.mapped_histogram)
    
    def _plot_default(self):
        plot = Plot(self.plot_data)
        plot.x_axis = None
        plot.y_axis = None
        plot.x_grid = None
        plot.y_grid = None
        plot.padding = 0
        plot.plot(('x', 'image_histogram'), render_style='connectedhold')
        plot.plot(('x', 'mapped_histogram'), type='filled_line', fill_color='yellow',
            render_style='connectedhold', name='mapped_histogram')

        low_overlay = AttributeLineOverlay(component=plot, model=self.unit_map,
            x_attr='low', orientation='vertical')
        high_overlay = AttributeLineOverlay(component=plot, model=self.unit_map,
            x_attr='high', orientation='vertical')
        low_tool = PlotDragTool(component=plot, model=self.unit_map,
                plot=low_overlay, x_attr='low', x_name='Low',
                x_bounds=(0, 'high'))
        high_tool = PlotDragTool(component=plot, model=self.unit_map,
                plot=high_overlay, x_attr='high', x_name='High',
                x_bounds=('low',1))

        intercept_tool = AttributeDragTool(component=plot, model=self.unit_map,
                x_attr='intercept')
        slope_tool = AttributeDragTool(component=plot, model=self.unit_map,
                x_attr='slope', modifier_keys=set(['shift']))
        gamma_tool = AttributeDragTool(component=plot, model=self.unit_map,
                x_attr='gamma', modifier_keys=set(['control']))
        plot.tools += [low_tool, high_tool, intercept_tool, slope_tool, gamma_tool]

        intercept_overlay = SimpleInspectorOverlay(component=plot, align='ul',
            inspector=intercept_tool,
            field_formatters=[[basic_formatter('Intercept', 2)]]
        )  
        slope_overlay = SimpleInspectorOverlay(component=plot, align='ul',
            inspector=slope_tool,
            field_formatters=[[basic_formatter('Slope', 2)]]
        )  
        gamma_overlay = SimpleInspectorOverlay(component=plot, align='ul',
            inspector=gamma_tool,
            field_formatters=[[basic_formatter('Gamma', 2)]]
        )  
        
        plot.overlays += [intercept_overlay, slope_overlay, gamma_overlay,
            low_overlay, high_overlay]
        return plot

    view = View(
        VGroup(
            Item('plot', editor=ComponentEditor()),
            show_labels=False
        ),
        resizable=True,
        height=32,
    )
    
    

class ImageView(HasTraits):
    """ A simple image plot
    
    """
    
    image_data = Array
    
    unit_map = Instance(UnitMap)
    
    histogram_view = Instance(HistogramView)
    
    plot_data = Instance(ArrayPlotData)
    
    plot = Instance(Plot)
    
    def map_changed(self):
        self.tcm.unit_func = self.unit_map.function
        self.plot.request_redraw()
    
    def _histogram_view_default(self):
        return HistogramView(image_data=self.image_data, unit_map=self.unit_map)
    
    def _unit_map_default(self):
        return UnitMap()
    
    def _plot_data_default(self):
        return ArrayPlotData(
            image=self.image_data,
        )
    
    def _plot_default(self):
        plot = Plot(self.plot_data)
        plot.x_axis = None
        plot.y_axis = None
        plot.padding = 0
        self.tcm = TransformColorMapper.from_color_map(gray)
        self.tcm.unit_func = self.unit_map.function
        self.unit_map.on_trait_change(self.map_changed, 'function')
        plot.img_plot('image', colormap=self.tcm)
        return plot
    
    view = View(
        VGroup(
            Item('plot', editor=ComponentEditor(), springy=True),
            Item('histogram_view', editor=InstanceEditor(), style='custom'),
            show_labels=False
        ),
        resizable=True
    )

if __name__ == '__main__':
    image_view = ImageView(image_data=moon())
    image_view.configure_traits()
