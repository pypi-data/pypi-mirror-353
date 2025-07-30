import json
from django.conf import settings as conf_settings


def sparta_a049a6ae10(type='gauge1') ->list:
    """
    GAUGE TYPE 1-2
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    gauge_data_dict = "{'min': 0, 'max': 100, 'value': 34}"
    options = """{
        "showTicks": True,
        "renderTicks": {
            "showTicks": True,
            "divisions": 10,
        },
    }"""
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to plot a simple gauge with gauge.js', 'sub_description':
        '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict}, 
  title=['{type} example'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with custom options', 'description':
        'Example to plot a simple gauge with gauge.js', 'sub_description':
        '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict}, 
  title=['{type} example'], 
  options={options},
  height=500
)
plot_example"""
        }]


def sparta_4230fc5911() ->list:
    return sparta_a049a6ae10(type='gauge1')


def sparta_2f1358810f() ->list:
    return sparta_a049a6ae10(type='gauge2')


def sparta_aca159b9a9() ->list:
    """
    GAUGE TYPE 3
    """
    type = 'gauge3'
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    gauge_data_dict = {'min': 0, 'max': 100, 'value': 34}
    options = """{
        "showTicks": True,
        "renderTicks": {
            "showTicks": True,
            "divisions": 10,
        },
        "zones":{"bInvertColor":True,"bMiddleColor":True,"colorLeft":"#20FF86","colorMiddle":"#F8E61C","colorRight":"#FF0000","maxHeightDeviation":5,"tiltZones":55}
    }"""
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to plot a simple gauge with gauge.js', 'sub_description':
        '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict}, 
  title=['Gauge3 example'], 
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom zones',
        'description': 'Example to plot a simple gauge with gauge.js',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict}, 
  gauge_zones=[0,10,30,80,100],
  title=['Gauge3 example'], 
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom zones and labels',
        'description': 'Example to plot a simple gauge with gauge.js',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict},
  gauge_zones=[0,10,30,80,100],
  gauge_zones_labels=['label 0','label 10','label 30','label 80','label 100'],
  title=['Gauge3 example'], 
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom options',
        'description': 'Example to plot a simple gauge with gauge.js',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict},
  gauge_zones=[0,10,30,80,100],
  title=['Gauge3 example'], 
  options={options},
  height=500
)
plot_example"""
        }]


def sparta_e8e8d007da() ->list:
    """
    GAUGE TYPE 4
    """
    type = 'gauge4'
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    gauge_data_dict = "{'min': 0, 'max': 100, 'value': 34}"
    options = """{
        "showTicks": True,
        "renderTicks": {
            "showTicks": True,
            "divisions": 10,
        },
        "zones":{"bInvertColor":True,"bMiddleColor":True,"colorLeft":"#20FF86","colorMiddle":"#F8E61C","colorRight":"#FF0000","maxHeightDeviation":5,"tiltZones":55}
    }"""
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to plot a simple gauge with gauge.js', 'sub_description':
        '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict}, 
  title=['Gauge4 example'], 
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom zones',
        'description': 'Example to plot a simple gauge with gauge.js',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict}, 
  gauge_zones=[0,10,30,80,100],
  title=['Gauge4 example'], 
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom zones and labels',
        'description': 'Example to plot a simple gauge with gauge.js',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict},
  gauge_zones=[0,10,30,80,100],
  gauge_zones_labels=['label 0','label 10','label 30','label 80','label 100'],
  title=['Gauge4 example'], 
  height=500
)
plot_example"""
        }, {'title':
        f'{type.capitalize()} with custom zones, labels and heights',
        'description': 'Example to plot a simple gauge with gauge.js',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict},
  gauge_zones=[0,10,30,80,100],
  gauge_zones_labels=['label 0','label 10','label 30','label 80','label 100'],
  gauge_zones_height=[2,6,10,14,18],
  title=['Gauge4 example'], 
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom options',
        'description': 'Example to plot a simple gauge with gauge.js',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
gauge_data_dict = {gauge_data_dict}
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  gauge={gauge_data_dict},
  gauge_zones=[0,10,30,80,100],
  title=['Gauge4 example'], 
  options={options},
  height=500
)
plot_example"""
        }]

#END OF QUBE
