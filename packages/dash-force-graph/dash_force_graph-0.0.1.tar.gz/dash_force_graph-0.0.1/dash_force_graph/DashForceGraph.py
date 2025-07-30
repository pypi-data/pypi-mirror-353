# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashForceGraph(Component):
    """A DashForceGraph component.
ForceGraph is a Dash component that wraps react-force-graph
for creating interactive force-directed graphs.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- backgroundClicked (dict; optional):
    Background click event (callback property).

- backgroundColor (string; default '#ffffff'):
    Canvas background color.

- className (string; optional):
    CSS class name.

- clickedLink (dict; optional):
    Clicked link data (callback property).

- clickedNode (dict; optional):
    Clicked node data (callback property).

- cooldownTicks (number; default 100):
    Number of layout engine cycles to run after render.

- cooldownTime (number; default 15000):
    Time (ms) to run the layout engine for.

- d3AlphaDecay (number; default 0.0228):
    D3 force simulation alpha decay rate.

- d3VelocityDecay (number; default 0.4):
    D3 force simulation velocity decay rate.

- enableNodeDrag (boolean; default True):
    Enable node dragging.

- enablePanInteraction (boolean; default True):
    Enable pan interaction.

- enableZoomInteraction (boolean; default True):
    Enable zoom interaction.

- graphData (dict; optional):
    Graph data structure with nodes and links.

    `graphData` is a dict with keys:

    - nodes (list of dicts; optional)

    - links (list of dicts; optional)

- height (number; default 600):
    Canvas height in pixels.

- hoveredNode (dict; optional):
    Hovered node data (callback property).

- is3D (boolean; default False):
    Whether to render as 3D graph.

- linkColor (string; default '#999999'):
    Link color.

- linkDirectionalArrowColor (string; default '#999999'):
    Link directional arrow color.

- linkDirectionalArrowLength (number; default 0):
    Link directional arrow length.

- linkDirectionalParticles (number; default 0):
    Link directional particles.

- linkWidth (number; default 1):
    Link width.

- nodeAutoColorBy (string; optional):
    Node property to automatically color nodes by.

- nodeColor (string; default '#1f77b4'):
    Node color (string or function).

- nodeLabel (string; default 'id'):
    Node label property or function.

- nodeSize (number | string; default 4):
    Node size (number, string, or function).

- style (dict; optional):
    CSS style object.

- warmupTicks (number; default 0):
    Number of warmup ticks before starting cooldown.

- width (number; default 800):
    Canvas width in pixels.

- zoomToFit (boolean; default False):
    Trigger zoom to fit."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_force_graph'
    _type = 'DashForceGraph'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, graphData=Component.UNDEFINED, width=Component.UNDEFINED, height=Component.UNDEFINED, backgroundColor=Component.UNDEFINED, nodeAutoColorBy=Component.UNDEFINED, nodeColor=Component.UNDEFINED, nodeSize=Component.UNDEFINED, nodeLabel=Component.UNDEFINED, linkColor=Component.UNDEFINED, linkWidth=Component.UNDEFINED, linkDirectionalArrowLength=Component.UNDEFINED, linkDirectionalArrowColor=Component.UNDEFINED, linkDirectionalParticles=Component.UNDEFINED, enableNodeDrag=Component.UNDEFINED, enableZoomInteraction=Component.UNDEFINED, enablePanInteraction=Component.UNDEFINED, cooldownTicks=Component.UNDEFINED, cooldownTime=Component.UNDEFINED, d3AlphaDecay=Component.UNDEFINED, d3VelocityDecay=Component.UNDEFINED, warmupTicks=Component.UNDEFINED, is3D=Component.UNDEFINED, zoomToFit=Component.UNDEFINED, clickedNode=Component.UNDEFINED, clickedLink=Component.UNDEFINED, hoveredNode=Component.UNDEFINED, backgroundClicked=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'backgroundClicked', 'backgroundColor', 'className', 'clickedLink', 'clickedNode', 'cooldownTicks', 'cooldownTime', 'd3AlphaDecay', 'd3VelocityDecay', 'enableNodeDrag', 'enablePanInteraction', 'enableZoomInteraction', 'graphData', 'height', 'hoveredNode', 'is3D', 'linkColor', 'linkDirectionalArrowColor', 'linkDirectionalArrowLength', 'linkDirectionalParticles', 'linkWidth', 'nodeAutoColorBy', 'nodeColor', 'nodeLabel', 'nodeSize', 'style', 'warmupTicks', 'width', 'zoomToFit']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'backgroundClicked', 'backgroundColor', 'className', 'clickedLink', 'clickedNode', 'cooldownTicks', 'cooldownTime', 'd3AlphaDecay', 'd3VelocityDecay', 'enableNodeDrag', 'enablePanInteraction', 'enableZoomInteraction', 'graphData', 'height', 'hoveredNode', 'is3D', 'linkColor', 'linkDirectionalArrowColor', 'linkDirectionalArrowLength', 'linkDirectionalParticles', 'linkWidth', 'nodeAutoColorBy', 'nodeColor', 'nodeLabel', 'nodeSize', 'style', 'warmupTicks', 'width', 'zoomToFit']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashForceGraph, self).__init__(**args)
