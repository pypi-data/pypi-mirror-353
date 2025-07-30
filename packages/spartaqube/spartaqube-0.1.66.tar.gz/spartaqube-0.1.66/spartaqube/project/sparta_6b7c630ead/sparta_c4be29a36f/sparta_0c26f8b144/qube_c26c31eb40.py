def sparta_5543301330() ->dict:
    """
    Gauge Type 1
    """
    return {'animationSpeed': {'doc_description':
        'Speed of the animation for the gauge pointer movement', 'doc_type':
        'Float', 'doc_default': 32}, 'showTicks': {'doc_description':
        'Whether to display ticks on the gauge', 'doc_type': 'Boolean',
        'doc_default': False}, 'angle': {'doc_description':
        'Angle of the gauge, in radians', 'doc_type': 'Float',
        'doc_default': 0.15}, 'lineWidth': {'doc_description':
        'Width of the gauge line', 'doc_type': 'Float', 'doc_default': 0.44
        }, 'radiusScale': {'doc_description': 'Scale of the gauge radius',
        'doc_type': 'Float', 'doc_default': 1}, 'pointer': {
        'doc_description': 'Settings for the gauge pointer', 'doc_type':
        'Dictionary', 'doc_default': {'length': {'doc_description':
        'Length of the pointer', 'doc_type': 'Float', 'doc_default': 0.6},
        'strokeWidth': {'doc_description': 'Width of the pointer stroke',
        'doc_type': 'Float', 'doc_default': 0.025}, 'color': {
        'doc_description': 'Color of the pointer', 'doc_type': 'String',
        'doc_default': '#000000'}}}, 'limitMax': {'doc_description':
        'Limit the maximum value of the gauge', 'doc_type': 'Boolean',
        'doc_default': False}, 'limitMin': {'doc_description':
        'Limit the minimum value of the gauge', 'doc_type': 'Boolean',
        'doc_default': False}, 'colorStart': {'doc_description':
        'Starting color of the gauge', 'doc_type': 'String', 'doc_default':
        '#9E6FCF'}, 'colorStop': {'doc_description':
        'Ending color of the gauge', 'doc_type': 'String', 'doc_default':
        '#8FC0DA'}, 'strokeColor': {'doc_description':
        'Color of the gauge stroke', 'doc_type': 'String', 'doc_default':
        '#E0E0E0'}, 'generateGradient': {'doc_description':
        'Whether to generate a gradient for the gauge colors', 'doc_type':
        'Boolean', 'doc_default': True}, 'highDpiSupport': {
        'doc_description': 'Whether to support high DPI screens',
        'doc_type': 'Boolean', 'doc_default': True}, 'labels': {
        'doc_description': 'Settings for the labels on the gauge',
        'doc_type': 'Dictionary', 'doc_default': {'display': {
        'doc_description': 'Whether to display labels on the gauge',
        'doc_type': 'Boolean', 'doc_default': True}, 'labelNumber': {
        'doc_description': 'Number of labels to display on the gauge',
        'doc_type': 'Float', 'doc_default': 2}, 'size': {'doc_description':
        'Font size of the labels', 'doc_type': 'Float', 'doc_default': 13},
        'family': {'doc_description': 'Font family of the labels',
        'doc_type': 'String', 'doc_default': 'Arial'}, 'color': {
        'doc_description': 'Color of the labels', 'doc_type': 'String',
        'doc_default': '#000000'}}}, 'zones': {'doc_description':
        'Settings for the colored zones on the gauge', 'doc_type':
        'Dictionary', 'doc_default': {'bInvertColor': {'doc_description':
        'Whether to invert the zone colors', 'doc_type': 'Boolean',
        'doc_default': False}, 'bMiddleColor': {'doc_description':
        'Whether to use a middle color for the zones', 'doc_type':
        'Boolean', 'doc_default': True}, 'colorLeft': {'doc_description':
        'Color of the left zone', 'doc_type': 'String', 'doc_default':
        '#20FF86'}, 'colorMiddle': {'doc_description':
        'Color of the middle zone', 'doc_type': 'String', 'doc_default':
        '#F8E61C'}, 'colorRight': {'doc_description':
        'Color of the right zone', 'doc_type': 'String', 'doc_default':
        '#FF0000'}, 'maxHeightDeviation': {'doc_description':
        'Maximum height deviation for the zones', 'doc_type': 'Float',
        'doc_default': 5}, 'tiltZones': {'doc_description':
        'Tilt of the zones on the gauge', 'doc_type': 'Float',
        'doc_default': 55}}}}


def sparta_6e7fe584a8() ->dict:
    """
    Gauge Type 2
    """
    return {'animationSpeed': {'doc_description':
        'Speed of the animation for the gauge pointer movement', 'doc_type':
        'Float', 'doc_default': 32}, 'showTicks': {'doc_description':
        'Whether to display ticks on the gauge', 'doc_type': 'Boolean',
        'doc_default': False}, 'angle': {'doc_description':
        'Angle of the gauge, in radians', 'doc_type': 'Float',
        'doc_default': 0}, 'lineWidth': {'doc_description':
        'Width of the gauge line', 'doc_type': 'Float', 'doc_default': 0.06
        }, 'pointer': {'doc_description': 'Settings for the gauge pointer',
        'doc_type': 'Dictionary', 'doc_default': {'length': {
        'doc_description': 'Length of the pointer', 'doc_type': 'Float',
        'doc_default': 0.6}, 'strokeWidth': {'doc_description':
        'Width of the pointer stroke', 'doc_type': 'Float', 'doc_default': 
        0.05}, 'color': {'doc_description': 'Color of the pointer',
        'doc_type': 'String', 'doc_default': '#000000'}}}, 'limitMax': {
        'doc_description': 'Limit the maximum value of the gauge',
        'doc_type': 'Boolean', 'doc_default': False}, 'limitMin': {
        'doc_description': 'Limit the minimum value of the gauge',
        'doc_type': 'Boolean', 'doc_default': False}, 'strokeColor': {
        'doc_description': 'Color of the gauge stroke', 'doc_type':
        'String', 'doc_default': '#E0E0E0'}, 'highDpiSupport': {
        'doc_description': 'Whether to support high DPI screens',
        'doc_type': 'Boolean', 'doc_default': True}, 'labels': {
        'doc_description': 'Settings for the labels on the gauge',
        'doc_type': 'Dictionary', 'doc_default': {'display': {
        'doc_description': 'Whether to display labels on the gauge',
        'doc_type': 'Boolean', 'doc_default': True}, 'labelNumber': {
        'doc_description': 'Number of labels to display on the gauge',
        'doc_type': 'Float', 'doc_default': 2}, 'size': {'doc_description':
        'Font size of the labels', 'doc_type': 'Float', 'doc_default': 13},
        'family': {'doc_description': 'Font family of the labels',
        'doc_type': 'String', 'doc_default': 'Arial'}, 'color': {
        'doc_description': 'Color of the labels', 'doc_type': 'String',
        'doc_default': '#000000'}}}, 'zones': {'doc_description':
        'Settings for the colored zones on the gauge', 'doc_type':
        'Dictionary', 'doc_default': {'bInvertColor': {'doc_description':
        'Whether to invert the zone colors', 'doc_type': 'Boolean',
        'doc_default': False}, 'bMiddleColor': {'doc_description':
        'Whether to use a middle color for the zones', 'doc_type':
        'Boolean', 'doc_default': True}, 'colorLeft': {'doc_description':
        'Color of the left zone', 'doc_type': 'String', 'doc_default':
        '#20FF86'}, 'colorMiddle': {'doc_description':
        'Color of the middle zone', 'doc_type': 'String', 'doc_default':
        '#F8E61C'}, 'colorRight': {'doc_description':
        'Color of the right zone', 'doc_type': 'String', 'doc_default':
        '#FF0000'}, 'maxHeightDeviation': {'doc_description':
        'Maximum height deviation for the zones', 'doc_type': 'Float',
        'doc_default': 5}, 'tiltZones': {'doc_description':
        'Tilt of the zones on the gauge', 'doc_type': 'Float',
        'doc_default': 55}}}, 'dataLabels': {'doc_description':
        'Settings for the data labels displayed on the gauge', 'doc_type':
        'Dictionary', 'doc_default': {'labels': {'doc_description':
        'List of labels to display on the gauge', 'doc_type': 'List',
        'doc_default': '[]'}, 'displayDatalabels': {'doc_description':
        'Whether to display data labels on the gauge', 'doc_type':
        'Boolean', 'doc_default': True}, 'colorDatalabels': {
        'doc_description': 'Color of the data labels', 'doc_type': 'String',
        'doc_default': '#191919'}, 'familyDatalabels': {'doc_description':
        'Font family of the data labels', 'doc_type': 'String',
        'doc_default': 'Arial'}, 'sizeDatalabels': {'doc_description':
        'Size of the data labels', 'doc_type': 'Float', 'doc_default': 12}}
        }, 'gaugeValue': {'doc_description':
        'Settings for the gauge value display', 'doc_type': 'Dictionary',
        'doc_default': {'display': {'doc_description':
        'Whether to display the gauge value', 'doc_type': 'Boolean',
        'doc_default': True}, 'prefix': {'doc_description':
        'Prefix to display before the gauge value', 'doc_type': 'String',
        'doc_default': ''}, 'suffix': {'doc_description':
        'Suffix to display after the gauge value', 'doc_type': 'String',
        'doc_default': ''}, 'color': {'doc_description':
        'Color of the gauge value', 'doc_type': 'String', 'doc_default':
        '#191919'}, 'family': {'doc_description':
        'Font family of the gauge value', 'doc_type': 'String',
        'doc_default': 'Arial'}, 'style': {'doc_description':
        'Font style of the gauge value', 'doc_type': 'String',
        'doc_default': 'normal'}, 'weight': {'doc_description':
        'Font weight of the gauge value', 'doc_type': 'String',
        'doc_default': 'normal'}, 'size': {'doc_description':
        'Font size of the gauge value', 'doc_type': 'Float', 'doc_default':
        12}, 'marginTop': {'doc_description':
        'Top margin for the gauge value', 'doc_type': 'Float',
        'doc_default': 0}, 'colorGaugeValue': {'doc_description':
        'Whether the gauge value color is enabled', 'doc_type': 'Boolean',
        'doc_default': True}}}}


def sparta_b449ac7f44() ->dict:
    """
    Gauge Type 3
    """
    return {'animationSpeed': {'doc_description':
        'Speed of the animation for the gauge pointer movement', 'doc_type':
        'Float', 'doc_default': 32}, 'showTicks': {'doc_description':
        'Whether to display ticks on the gauge', 'doc_type': 'Boolean',
        'doc_default': False}, 'angle': {'doc_description':
        'Angle of the gauge, in radians', 'doc_type': 'Float',
        'doc_default': -0.25}, 'lineWidth': {'doc_description':
        'Width of the gauge line', 'doc_type': 'Float', 'doc_default': 0.2},
        'pointer': {'doc_description': 'Settings for the gauge pointer',
        'doc_type': 'Dictionary', 'doc_default': {'length': {
        'doc_description': 'Length of the pointer', 'doc_type': 'Float',
        'doc_default': 0.6}, 'strokeWidth': {'doc_description':
        'Width of the pointer stroke', 'doc_type': 'Float', 'doc_default': 
        0.025}, 'color': {'doc_description': 'Color of the pointer',
        'doc_type': 'String', 'doc_default': '#000000'}}}, 'limitMax': {
        'doc_description': 'Limit the maximum value of the gauge',
        'doc_type': 'Boolean', 'doc_default': False}, 'limitMin': {
        'doc_description': 'Limit the minimum value of the gauge',
        'doc_type': 'Boolean', 'doc_default': False}, 'colorStart': {
        'doc_description': 'Starting color of the gauge', 'doc_type':
        'String', 'doc_default': '#9E6FCF'}, 'colorStop': {
        'doc_description': 'Ending color of the gauge', 'doc_type':
        'String', 'doc_default': '#8FC0DA'}, 'strokeColor': {
        'doc_description': 'Color of the gauge stroke', 'doc_type':
        'String', 'doc_default': '#E0E0E0'}, 'highDpiSupport': {
        'doc_description': 'Whether to support high DPI screens',
        'doc_type': 'Boolean', 'doc_default': True}, 'labels': {
        'doc_description': 'Settings for the labels on the gauge',
        'doc_type': 'Dictionary', 'doc_default': {'display': {
        'doc_description': 'Whether to display labels on the gauge',
        'doc_type': 'Boolean', 'doc_default': True}, 'labelNumber': {
        'doc_description': 'Number of labels to display on the gauge',
        'doc_type': 'Float', 'doc_default': 2}, 'size': {'doc_description':
        'Font size of the labels', 'doc_type': 'Float', 'doc_default': 13},
        'family': {'doc_description': 'Font family of the labels',
        'doc_type': 'String', 'doc_default': 'Arial'}, 'color': {
        'doc_description': 'Color of the labels', 'doc_type': 'String',
        'doc_default': '#000000'}}}, 'zones': {'doc_description':
        'Settings for the colored zones on the gauge', 'doc_type':
        'Dictionary', 'doc_default': {'bInvertColor': {'doc_description':
        'Whether to invert the zone colors', 'doc_type': 'Boolean',
        'doc_default': False}, 'bMiddleColor': {'doc_description':
        'Whether to use a middle color for the zones', 'doc_type':
        'Boolean', 'doc_default': True}, 'colorLeft': {'doc_description':
        'Color of the left zone', 'doc_type': 'String', 'doc_default':
        '#20FF86'}, 'colorMiddle': {'doc_description':
        'Color of the middle zone', 'doc_type': 'String', 'doc_default':
        '#F8E61C'}, 'colorRight': {'doc_description':
        'Color of the right zone', 'doc_type': 'String', 'doc_default':
        '#FF0000'}, 'maxHeightDeviation': {'doc_description':
        'Maximum height deviation for the zones', 'doc_type': 'Float',
        'doc_default': 5}, 'tiltZones': {'doc_description':
        'Tilt of the zones on the gauge', 'doc_type': 'Float',
        'doc_default': 55}}}, 'dataLabels': {'doc_description':
        'Settings for the data labels displayed on the gauge', 'doc_type':
        'Dictionary', 'doc_default': {'labels': {'doc_description':
        'List of labels to display on the gauge', 'doc_type': 'List',
        'doc_default': '[]'}, 'displayDatalabels': {'doc_description':
        'Whether to display data labels on the gauge', 'doc_type':
        'Boolean', 'doc_default': True}, 'colorDatalabels': {
        'doc_description': 'Color of the data labels', 'doc_type': 'String',
        'doc_default': '#191919'}, 'familyDatalabels': {'doc_description':
        'Font family of the data labels', 'doc_type': 'String',
        'doc_default': 'Arial'}, 'sizeDatalabels': {'doc_description':
        'Size of the data labels', 'doc_type': 'Float', 'doc_default': 12}}}}


def sparta_c224f94e02() ->dict:
    """
    Gauge Type 4
    """
    return {'animationSpeed': {'doc_description':
        'Speed of the animation for the gauge pointer movement', 'doc_type':
        'Float', 'doc_default': 32}, 'showTicks': {'doc_description':
        'Whether to display ticks on the gauge', 'doc_type': 'Boolean',
        'doc_default': False}, 'angle': {'doc_description':
        'Angle of the gauge, in radians', 'doc_type': 'Float',
        'doc_default': 0.1}, 'lineWidth': {'doc_description':
        'Width of the gauge line', 'doc_type': 'Float', 'doc_default': 0.3},
        'radiusScale': {'doc_description': 'Scale of the gauge radius',
        'doc_type': 'Float', 'doc_default': 1}, 'pointer': {
        'doc_description': 'Settings for the gauge pointer', 'doc_type':
        'Dictionary', 'doc_default': {'length': {'doc_description':
        'Length of the pointer', 'doc_type': 'Float', 'doc_default': 0.6},
        'strokeWidth': {'doc_description': 'Width of the pointer stroke',
        'doc_type': 'Float', 'doc_default': 0.025}, 'color': {
        'doc_description': 'Color of the pointer', 'doc_type': 'String',
        'doc_default': '#000000'}}}, 'limitMax': {'doc_description':
        'Limit the maximum value of the gauge', 'doc_type': 'Boolean',
        'doc_default': False}, 'limitMin': {'doc_description':
        'Limit the minimum value of the gauge', 'doc_type': 'Boolean',
        'doc_default': False}, 'colorStart': {'doc_description':
        'Starting color of the gauge', 'doc_type': 'String', 'doc_default':
        '#9E6FCF'}, 'colorStop': {'doc_description':
        'Ending color of the gauge', 'doc_type': 'String', 'doc_default':
        '#8FC0DA'}, 'strokeColor': {'doc_description':
        'Color of the gauge stroke', 'doc_type': 'String', 'doc_default':
        '#E0E0E0'}, 'highDpiSupport': {'doc_description':
        'Whether to support high DPI screens', 'doc_type': 'Boolean',
        'doc_default': True}, 'labels': {'doc_description':
        'Settings for the labels on the gauge', 'doc_type': 'Dictionary',
        'doc_default': {'display': {'doc_description':
        'Whether to display labels on the gauge', 'doc_type': 'Boolean',
        'doc_default': True}, 'labelNumber': {'doc_description':
        'Number of labels to display on the gauge', 'doc_type': 'Float',
        'doc_default': 2}, 'size': {'doc_description':
        'Font size of the labels', 'doc_type': 'Float', 'doc_default': 13},
        'family': {'doc_description': 'Font family of the labels',
        'doc_type': 'String', 'doc_default': 'Arial'}, 'color': {
        'doc_description': 'Color of the labels', 'doc_type': 'String',
        'doc_default': '#000000'}}}, 'zones': {'doc_description':
        'Settings for the colored zones on the gauge', 'doc_type':
        'Dictionary', 'doc_default': {'bInvertColor': {'doc_description':
        'Whether to invert the zone colors', 'doc_type': 'Boolean',
        'doc_default': False}, 'bMiddleColor': {'doc_description':
        'Whether to use a middle color for the zones', 'doc_type':
        'Boolean', 'doc_default': True}, 'colorLeft': {'doc_description':
        'Color of the left zone', 'doc_type': 'String', 'doc_default':
        '#20FF86'}, 'colorMiddle': {'doc_description':
        'Color of the middle zone', 'doc_type': 'String', 'doc_default':
        '#F8E61C'}, 'colorRight': {'doc_description':
        'Color of the right zone', 'doc_type': 'String', 'doc_default':
        '#FF0000'}, 'maxHeightDeviation': {'doc_description':
        'Maximum height deviation for the zones', 'doc_type': 'Float',
        'doc_default': 5}, 'tiltZones': {'doc_description':
        'Tilt of the zones on the gauge', 'doc_type': 'Float',
        'doc_default': 55}}}, 'dataLabels': {'doc_description':
        'Settings for the data labels displayed on the gauge', 'doc_type':
        'Dictionary', 'doc_default': {'labels': {'doc_description':
        'List of labels to display on the gauge', 'doc_type': 'List',
        'doc_default': '[]'}, 'displayDatalabels': {'doc_description':
        'Whether to display data labels on the gauge', 'doc_type':
        'Boolean', 'doc_default': True}, 'colorDatalabels': {
        'doc_description': 'Color of the data labels', 'doc_type': 'String',
        'doc_default': '#191919'}, 'familyDatalabels': {'doc_description':
        'Font family of the data labels', 'doc_type': 'String',
        'doc_default': 'Arial'}, 'sizeDatalabels': {'doc_description':
        'Size of the data labels', 'doc_type': 'Float', 'doc_default': 12}}}}

#END OF QUBE
