import os, sys, re
from django.conf import settings
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_0c26f8b144.qube_ebbb432987 as qube_ebbb432987
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_0c26f8b144.qube_4858e1e7db as qube_4858e1e7db
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_0c26f8b144.qube_c26c31eb40 as qube_c26c31eb40
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_0c26f8b144.qube_84ed70686b as qube_84ed70686b
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_70dacc68fe.qube_588be94b04 as qube_588be94b04
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_70dacc68fe.qube_0014fd4204 as qube_0014fd4204
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_70dacc68fe.qube_ace1d6e9fa as qube_ace1d6e9fa
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_70dacc68fe.qube_966b5e661c as qube_966b5e661c
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_70dacc68fe.qube_59b2cfc87f as qube_59b2cfc87f
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_70dacc68fe.qube_2cc46dbb53 as qube_2cc46dbb53
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_70dacc68fe.qube_61bde0b72f as qube_61bde0b72f
import project.sparta_6b7c630ead.sparta_c4be29a36f.sparta_70dacc68fe.qube_60bc8c5499 as qube_60bc8c5499


def sparta_b770ba5f34(b_return_type_id=False) ->list:
    """
    Return list of available plot type (for api)
    """

    def extract_values_by_key(input_string, key='typeId'):
        escaped_key = re.escape(key)
        pattern = f'\'{escaped_key}\':\\s*(true|false|\\d+|\'.*?\'|\\".*?\\")'
        matches = re.findall(pattern, input_string, re.IGNORECASE)
        values = [m.strip('\'"') for m in matches]
        return values

    def parse_js_file(file_path) ->list:
        with open(file_path, 'r') as file:
            content = file.read()
        content = content.split('// PARSED ENDLINE COMMENT (DO NOT REMOVE)')[0]
        js_content = content
        match = re.search('return\\s*({[\\s\\S]*?});', js_content)
        if not match:
            raise ValueError('No return dictionary found in the file.')
        js_dict_str = match.group(1)
        typeid_list = extract_values_by_key(js_dict_str, 'typeId')
        slug_api_list = extract_values_by_key(js_dict_str, 'slugApi')
        display_list = extract_values_by_key(js_dict_str, 'display')
        name_list = extract_values_by_key(js_dict_str, 'name')
        library_list = extract_values_by_key(js_dict_str, 'libraryName')
        plot_types = []
        cnt = 0
        for idx, _ in enumerate(typeid_list):
            if display_list[idx] == 'true':
                slug_api = slug_api_list[idx]
                if slug_api != '-1' and len(slug_api) > 0:
                    tmp_dict = {'ID': slug_api_list[idx], 'Name': name_list
                        [idx], 'Library': library_list[idx]}
                    if b_return_type_id or True:
                        tmp_dict['type_plot'] = typeid_list[idx]
                    plot_types.append(tmp_dict)
                    cnt += 1
        return plot_types
    current_path = os.path.dirname(__file__)
    core_path = os.path.dirname(current_path)
    project_path = os.path.dirname(core_path)
    main_path = os.path.dirname(project_path)
    if settings.DEBUG:
        static_path = os.path.join(main_path, 'static')
    else:
        static_path = os.path.join(main_path, 'staticfiles')
    file_path = os.path.join(static_path,
        'js/vueComponent/plot-db/new-plot/plot-config/plotConfigMixin.js')
    if not os.path.exists(file_path):
        file_path = os.path.join(static_path, 'js/util/plotConfigMixin.js')
    file_path = os.path.normpath(file_path)
    plot_types: list = parse_js_file(file_path)
    return plot_types


def sparta_02318b41b3() ->dict:
    """
    
    """
    argument_descriptions_mapper = {'x': {'type': ['list',
        'DataFrame Index'], 'description':
        'list or DataFrame index representing the x axis of your chart'},
        'y': {'type': ['list', 'list[list]', 'pd.DataFrame',
        '[pd.Series, pd.Series...]'], 'description':
        'list, list of lists, DataFrame, or list of Series representing the lines to plot'
        }, 'r': {'type': ['list', 'list[list]', 'pd.DataFrame',
        '[pd.Series, pd.Series...]'], 'description':
        'list, list of lists, DataFrame, or list of Series representing the radius to plot'
        }, 'stacked': {'type': ['boolean'], 'description':
        'If True and multiple series, all the series will be stacked together'
        }, 'date_format': {'type': ['str'], 'description':
        'For instance: yyyy-MM-dd, dd/MM/yyyy, yyyy-MM-dd HH:MM:SS etc... year: y, month: M, day: d, quarter: QQQ, week: w, hour: HH, minute: MM, seconds: SS, millisecond: ms'
        }, 'legend': {'type': ['list'], 'description':
        "A list containing the names of each series in your chart. Each element in the list corresponds to the name of a series, which will be displayed in the chart's legend."
        }, 'labels': {'type': ['list', 'list[list]'], 'description':
        'A list or list of lists containing the labels for each point (scatter/bubble chart).'
        }, 'ohlcv': {'type': ['pd.DataFrame()',
        '[open:list, high:list, low:list, close:list, volume:list]',
        '[open:pd.Series, high:pd.Series, low:pd.Series, close:pd.Series, volume:pd.Series]'
        ], 'description':
        'DataFrame with Open, High, Low, Close and optionally Volumes columns. Or a list containing eight list or pd.Series of Open, High, Low, Close and optionally volumes.'
        }, 'shaded_background': {'type': ['list', 'list[list]',
        'pd.DataFrame', '[pd.Series, pd.Series...]'], 'description':
        'The shaded_background input should be a list of numerical values representing the intensity levels of the shaded background, where each value corresponds to a specific color gradient'
        }, 'datalabels': {'type': ['list', 'list[list]'], 'description':
        'For charts containing a single series, provide a list of strings to represent the label of each point. If your chart includes multiple series, supply a list of lists, where each inner list specifies the labels for the points on each corresponding series'
        }, 'border': {'type': ['list', 'list[list]'], 'description':
        'For charts containing a single series, provide a list of color strings (in hex, rgb, or rgba format) to represent the border color of each point. If your chart includes multiple series, supply a list of lists, where each inner list specifies the border colors for the points on each corresponding series'
        }, 'background': {'type': ['list', 'list[list]'], 'description':
        'For charts containing a single series, provide a list of color strings (in hex, rgb, or rgba format) to represent the background color of each point. If your chart includes multiple series, supply a list of lists, where each inner list specifies the background colors for the points on each corresponding series'
        }, 'tooltips_title': {'type': ['list', 'list[list]'], 'description':
        'For charts containing a single series, provide a list of strings to represent the tooltip title of each point. If your chart includes multiple series, supply a list of lists, where each inner list specifies the tooltips for the points on each corresponding series'
        }, 'tooltips_label': {'type': ['list', 'list[list]'], 'description':
        'For charts containing a single series, provide a list of strings to represent the tooltip label of each point. If your chart includes multiple series, supply a list of lists, where each inner list specifies the tooltips for the points on each corresponding series'
        }, 'border_style': {'type': ['list', 'list[list]'], 'description':
        'For charts containing a single series, provide a list of strings to represent the border style of each point. If your chart includes multiple series, supply a list of lists, where each inner list specifies the border styles for the points on each corresponding series. Please make sure to only use border styles from the following list: <span style="font-weight:bold">"solid", "dotted", "dashed", "largeDashed", "sparseDotted"</span>.'
        }, 'chart_type': {'type': ['str'], 'description':
        'This is the type of the chart. You can find the available ID by running the get_plot_types()'
        }, 'gauge': {'type': ['dict'], 'description':
        "This dictionary must contains 3 keys: <span style='font-weight:bold'>'value'</span> that corresponds to the value of the gauge, <span style='font-weight:bold'>'min'</span> and <span style='font-weight:bold'>'max'</span> for the minimum and maximum value the gauge can take"
        }, 'interactive': {'type': ['boolean'], 'description':
        'If set to false, only the final plot will be displayed, without the option for interactive editing. Default value is true.'
        }, 'dataframe': {'type': [], 'description': ''}, 'dates': {'type':
        ['list', 'DataFrame Index'], 'description':
        'list or DataFrame index representing the dates of your time series'
        }, 'returns': {'type': ['list', 'pd.DataFrame', 'pd.Series'],
        'description':
        'list, DataFrame, or Series representing the (portfolio) returns of your time series'
        }, 'returns_bmk': {'type': ['list', 'pd.DataFrame', 'pd.Series'],
        'description':
        'list, DataFrame, or Series representing the (benchmark) returns of your time series'
        }, 'title': {'type': ['str'], 'description': 'Title of your plot'},
        'title_css': {'type': ['dict'], 'description':
        'Apply css to your title. Put all your css attributes into a dictionary. For instance: {"text-align": "center", "color": "red"} etc...'
        }, 'options': {'type': ['dict'], 'description':
        'You can override every attributes of the chart with the highest granularity in this options dictionary. Please refer to the option section below to find out more about all the attributes to override'
        }, 'width': {'type': ['int', 'str'], 'description':
        'This is the width of the widget. You can either specify an integer or a string with the percentage value (width="100%" for instance)'
        }, 'height': {'type': ['int', 'str'], 'description':
        'This is the height of the widget. You can either specify an integer or a string with the percentage value (height="100%" for instance)'
        }, 'gauge_zones': {'type': ['list'], 'description':
        'Separate the background sectors or zones to have static colors'},
        'gauge_zones_labels': {'type': ['list'], 'description':
        'Set labels for each zones'}, 'gauge_zones_height': {'type': [
        'list'], 'description':
        'Height parameter may be passed in to increase the size for each zone'}
        }
    vectorized_optional = {'datalabels': argument_descriptions_mapper[
        'datalabels'], 'border': argument_descriptions_mapper['border'],
        'background': argument_descriptions_mapper['background'],
        'tooltips_title': argument_descriptions_mapper['tooltips_title'],
        'tooltips_label': argument_descriptions_mapper['tooltips_label'],
        'border_style': argument_descriptions_mapper['border_style']}
    dimension_optional = {'width': argument_descriptions_mapper['width'],
        'height': argument_descriptions_mapper['height']}
    title_optional = {'title': argument_descriptions_mapper['title'],
        'title_css': argument_descriptions_mapper['title_css']}
    dataframe_dict = {'signature':
        "def plot(dataframe:list, chart_type='dataframe', title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
        , 'description': '', 'mandatory_args': {'dataframe':
        argument_descriptions_mapper['dataframe']}, 'optional_args': {**
        title_optional, **{'options': argument_descriptions_mapper[
        'options']}, **dimension_optional}}
    quantstats_dict = {'signature':
        "def plot(dates:list, returns:list, chart_type='quantstats', returns_bmk:list=None, title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
        , 'description': '', 'mandatory_args': {'dates':
        argument_descriptions_mapper['dates'], 'returns':
        argument_descriptions_mapper['returns']}, 'optional_args': {**{
        'returns_bmk': argument_descriptions_mapper['returns_bmk'],
        'options': argument_descriptions_mapper['options']}, **
        title_optional, **dimension_optional}}
    notebook_dict = {'signature':
        "def plot(chart_type='notebook', title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
        , 'description': '', 'mandatory_args': {'dataframe':
        argument_descriptions_mapper['dataframe']}, 'optional_args': {**
        title_optional, **dimension_optional}}
    dynamic_rescale_dict = {'signature':
        "def plot(chart_type='dynamicRescale', title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
        , 'description': '', 'mandatory_args': {'x':
        argument_descriptions_mapper['x'], 'y':
        argument_descriptions_mapper['y']}, 'optional_args': {**
        title_optional, **dimension_optional}}
    regression_dict = {'signature':
        "def plot(chart_type='regression', title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
        , 'description': '', 'mandatory_args': {'x':
        argument_descriptions_mapper['x'], 'y':
        argument_descriptions_mapper['y']}, 'optional_args': {**
        title_optional, **dimension_optional}}
    calendar_dict = {'signature':
        "def plot(chart_type='calendar', title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
        , 'description': '', 'mandatory_args': {'x':
        argument_descriptions_mapper['x'], 'y':
        argument_descriptions_mapper['y']}, 'optional_args': {**
        title_optional, **dimension_optional}}
    wordcloud_dict = {'signature':
        "def plot(chart_type='wordcloud', title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
        , 'description': '', 'mandatory_args': {'x':
        argument_descriptions_mapper['x'], 'y':
        argument_descriptions_mapper['y']}, 'optional_args': {**
        title_optional, **dimension_optional}}
    summary_statistics_dict = {'signature':
        "def plot(y:list, chart_type='summary_statistics', title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
        , 'description': '', 'mandatory_args': {'y':
        argument_descriptions_mapper['y']}, 'optional_args': {**
        title_optional, **{'options': argument_descriptions_mapper[
        'options']}, **dimension_optional}}

    def get_chart_js_input(chart_type='line'):
        """
        
        """
        if chart_type in ['scatter', 'bubble']:
            inputs_dict = {'signature':
                f"""def plot(x:list, y:list, legend:list=None, date_format:str=None, labels:list=None, datalabels:list=None, 
        border:list=None, background:list=None, tooltips_title:list=None, tooltips_label:list=None, 
        border_style:list=None, chart_type='{chart_type}', interactive=True, title:str=None, title_css:dict=None,
        options:dict=None, width='60%', height=750)"""
                , 'description': '', 'mandatory_args': {'x':
                argument_descriptions_mapper['x'], 'y':
                argument_descriptions_mapper['y']}, 'optional_args': {**
                title_optional, **{'date_format':
                argument_descriptions_mapper['date_format'], 'interactive':
                argument_descriptions_mapper['interactive'], 'options':
                argument_descriptions_mapper['options'], 'legend':
                argument_descriptions_mapper['legend'], 'labels':
                argument_descriptions_mapper['labels']}, **
                vectorized_optional, **dimension_optional}}
        elif chart_type in ['bar', 'area']:
            inputs_dict = {'signature':
                f"""def plot(x:list, y:list, stacked:bool=False, legend:list=None, date_format:str=None, datalabels:list=None, 
        border:list=None, background:list=None, tooltips_title:list=None, tooltips_label:list=None, 
        border_style:list=None, chart_type='{chart_type}', interactive=True, title:str=None, title_css:dict=None,
        options:dict=None, width='60%', height=750)"""
                , 'description': '', 'mandatory_args': {'x':
                argument_descriptions_mapper['x'], 'y':
                argument_descriptions_mapper['y']}, 'optional_args': {**
                title_optional, **{'date_format':
                argument_descriptions_mapper['date_format'], 'stacked':
                argument_descriptions_mapper['stacked'], 'interactive':
                argument_descriptions_mapper['interactive'], 'options':
                argument_descriptions_mapper['options'], 'legend':
                argument_descriptions_mapper['legend']}, **
                vectorized_optional, **dimension_optional}}
        else:
            inputs_dict = {'signature':
                f"""def plot(x:list, y:list, legend:list=None, date_format:str=None, datalabels:list=None, 
        border:list=None, background:list=None, tooltips_title:list=None, tooltips_label:list=None, 
        border_style:list=None, chart_type='{chart_type}', interactive=True, title:str=None, title_css:dict=None,
        options:dict=None, width='60%', height=750)"""
                , 'description': '', 'mandatory_args': {'x':
                argument_descriptions_mapper['x'], 'y':
                argument_descriptions_mapper['y']}, 'optional_args': {**
                title_optional, **{'date_format':
                argument_descriptions_mapper['date_format'], 'interactive':
                argument_descriptions_mapper['interactive'], 'options':
                argument_descriptions_mapper['options'], 'legend':
                argument_descriptions_mapper['legend']}, **
                vectorized_optional, **dimension_optional}}
        return inputs_dict

    def get_tv_input(chart_type='realTimeStock'):
        return {'signature':
            f"def plot(chart_type='{chart_type}', title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
            , 'description': '', 'mandatory_args': {}, 'optional_args': {**
            title_optional, **{'options': argument_descriptions_mapper[
            'options'], **dimension_optional}}}

    def get_lightweight_input(chart_type='ts_line'):
        if chart_type == 'ts_shaded':
            inputs_dict = {'signature':
                f"""def plot(x:list, y:list, shaded_background:list, legend:list=None, chart_type='{chart_type}', title:str=None, title_css:dict=None, 
    options:dict=None, width='60%', height=750)"""
                , 'description': '', 'mandatory_args': {'x':
                argument_descriptions_mapper['x'], 'y':
                argument_descriptions_mapper['y'], 'shaded_background':
                argument_descriptions_mapper['shaded_background']},
                'optional_args': {**{'options':
                argument_descriptions_mapper['options'], 'legend':
                argument_descriptions_mapper['legend']}, **dimension_optional}}
        elif chart_type == 'candlestick':
            inputs_dict = {'signature':
                f"""def plot(x:list, ohlcv:list, legend:list=None, chart_type='{chart_type}', title:str=None, title_css:dict=None,
    options:dict=None, width='60%', height=750)"""
                , 'description': '', 'mandatory_args': {'x':
                argument_descriptions_mapper['x'], 'ohlcv':
                argument_descriptions_mapper['y']}, 'optional_args': {**
                title_optional, **{'options': argument_descriptions_mapper[
                'options'], 'legend': argument_descriptions_mapper['legend'
                ]}, **dimension_optional}}
        else:
            inputs_dict = {'signature':
                f"""def plot(x:list, y:list, legend:list=None, chart_type='{chart_type}', title:str=None, title_css:dict=None,
    options:dict=None, width='60%', height=750)"""
                , 'description': '', 'mandatory_args': {'x':
                argument_descriptions_mapper['x'], 'y':
                argument_descriptions_mapper['y']}, 'optional_args': {**
                title_optional, **{'options': argument_descriptions_mapper[
                'options'], 'legend': argument_descriptions_mapper['legend'
                ]}, **dimension_optional}}
        return inputs_dict

    def get_gauge_input(chart_type='gauge1'):
        signature = ("def plot(chart_type='" + str(chart_type) +
            "', gauge={'value':10, 'min':1, 'max':100}, title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
            )
        optional_args = {**{'options': argument_descriptions_mapper[
            'options'], **dimension_optional}}
        if chart_type == 'gauge3':
            optional_args = {**{'gauge_zones': argument_descriptions_mapper
                ['gauge_zones'], 'gauge_zones_labels':
                argument_descriptions_mapper['gauge_zones_labels']}, **
                title_optional, **{'options': argument_descriptions_mapper[
                'options']}, **dimension_optional}
            signature = ("def plot(chart_type='" + str(chart_type) +
                "', gauge={'value':10, 'min':1, 'max':100}, gauge_zones:list=None, gauge_zones_labels:list=None, title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
                )
        elif chart_type == 'gauge4':
            optional_args = {'gauge_zones': argument_descriptions_mapper[
                'gauge_zones'], 'gauge_zones_labels':
                argument_descriptions_mapper['gauge_zones_labels'],
                'gauge_zones_height': argument_descriptions_mapper[
                'gauge_zones_height'], **title_optional, **{'options':
                argument_descriptions_mapper['options']}, **dimension_optional}
            signature = ("def plot(chart_type='" + str(chart_type) +
                "', gauge={'value':10, 'min':1, 'max':100}, gauge_zones:list=None, gauge_zones_labels:list=None, gauge_zones_height:list=None, title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
                )
        return {'signature': signature, 'description': '', 'mandatory_args':
            {'gauge': argument_descriptions_mapper['gauge']},
            'optional_args': {**title_optional, **optional_args}}

    def get_df_relationships_default(chart_type):
        return {'signature':
            f"def plot(chart_type='{chart_type}', title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
            , 'description': '', 'mandatory_args': {'x':
            argument_descriptions_mapper['x'], 'y':
            argument_descriptions_mapper['y']}, 'optional_args': {**
            title_optional, **dimension_optional}}

    def get_df_tsa_default(chart_type):
        return {'signature':
            f"def plot(chart_type='{chart_type}', title:str=None, title_css:dict=None, options:dict=None, width='60%', height=750)"
            , 'description': '', 'mandatory_args': {'x':
            argument_descriptions_mapper['x'], 'y':
            argument_descriptions_mapper['y']}, 'optional_args': {**
            title_optional, **dimension_optional}}
    inputs_options = {'line': {'input': get_chart_js_input('line'),
        'options': qube_4858e1e7db.sparta_ece2f26cb7(), 'examples':
        qube_588be94b04.sparta_9a4308f6f6()}, 'bar': {'input':
        get_chart_js_input('bar'), 'options': qube_4858e1e7db.sparta_ece2f26cb7(), 'examples': qube_588be94b04.sparta_3ab50def6c()},
        'area': {'input': get_chart_js_input('area'), 'options':
        qube_4858e1e7db.sparta_ece2f26cb7(), 'examples': qube_588be94b04.sparta_7e54e11f33()}, 'scatter': {'input': get_chart_js_input(
        'scatter'), 'options': qube_4858e1e7db.sparta_ece2f26cb7(),
        'examples': qube_588be94b04.sparta_577b615514()}, 'pie': {
        'input': get_chart_js_input('pie'), 'options': qube_4858e1e7db.sparta_ece2f26cb7(), 'examples': qube_588be94b04.sparta_999f59d5a5()},
        'donut': {'input': get_chart_js_input('donut'), 'options':
        qube_4858e1e7db.sparta_ece2f26cb7(), 'examples': qube_588be94b04.sparta_08b6dd8bf1()}, 'radar': {'input': get_chart_js_input(
        'radar'), 'options': qube_4858e1e7db.sparta_ece2f26cb7(), 'examples':
        qube_588be94b04.sparta_dfcf8a36ef()}, 'bubble': {'input':
        get_chart_js_input('bubble'), 'options': qube_4858e1e7db.sparta_ece2f26cb7(), 'examples': qube_588be94b04.sparta_a76181a12e
        ()}, 'barH': {'input': get_chart_js_input('barH'), 'options':
        qube_4858e1e7db.sparta_ece2f26cb7(), 'examples': qube_588be94b04.sparta_5e6988cc50()}, 'polar': {'input':
        get_chart_js_input('polar'), 'options': qube_4858e1e7db.sparta_ece2f26cb7(), 'examples': qube_588be94b04.sparta_83f52c96b7(
        )}, 'mixed': {'input': get_chart_js_input('mixed'), 'options':
        qube_4858e1e7db.sparta_ece2f26cb7(), 'examples': qube_588be94b04.sparta_b1b58a8051()}, 'matrix': {'input': get_chart_js_input(
        'matrix'), 'options': qube_4858e1e7db.sparta_ece2f26cb7(),
        'examples': qube_588be94b04.sparta_38bf5c9203()}, 'timescale': {
        'input': get_chart_js_input('timescale'), 'options':
        qube_4858e1e7db.sparta_ece2f26cb7(), 'examples': qube_588be94b04.sparta_3ab50def6c()}, 'histogram': {'input': get_chart_js_input(
        'histogram'), 'options': qube_4858e1e7db.sparta_ece2f26cb7(),
        'examples': qube_588be94b04.sparta_1545b34ec3()},
        'realTimeStock': {'input': get_tv_input('realTimeStock'), 'options':
        qube_ebbb432987.sparta_0669b53e6d(), 'examples':
        qube_966b5e661c.sparta_e3b4090eec()}, 'stockHeatmap': {
        'input': get_tv_input('stockHeatmap'), 'options': qube_ebbb432987.sparta_1107e3a1c1(), 'examples': qube_966b5e661c.sparta_42c4f3e28b()}, 'etfHeatmap': {'input': get_tv_input(
        'etfHeatmap'), 'options': qube_ebbb432987.sparta_17030b0b8d(),
        'examples': qube_966b5e661c.sparta_f91b062026()},
        'economicCalendar': {'input': get_tv_input('economicCalendar'),
        'options': qube_ebbb432987.sparta_9bdd5b6d04(), 'examples':
        qube_966b5e661c.sparta_1404bac267()}, 'cryptoTable': {
        'input': get_tv_input('cryptoTable'), 'options': qube_ebbb432987.sparta_d2d8f7ef79(), 'examples': qube_966b5e661c.sparta_2010ef85e6()}, 'cryptoHeatmap': {'input':
        get_tv_input('cryptoHeatmap'), 'options': qube_ebbb432987.sparta_f203138950(), 'examples': qube_966b5e661c.sparta_f64db7e561()}, 'forex': {'input': get_tv_input(
        'forex'), 'options': qube_ebbb432987.sparta_673f175814(), 'examples':
        qube_966b5e661c.sparta_dfec8591b7()}, 'forexHeatmap': {'input':
        get_tv_input('forexHeatmap'), 'options': qube_ebbb432987.sparta_fa9de7f4d9(), 'examples': qube_966b5e661c.sparta_dfec8591b7
        ('forexHeatmap')}, 'marketData': {'input': get_tv_input(
        'marketData'), 'options': qube_ebbb432987.sparta_7dd5028b04(),
        'examples': qube_966b5e661c.sparta_5e76fe802c()},
        'stockMarket': {'input': get_tv_input('stockMarket'), 'options':
        qube_ebbb432987.sparta_f192d265cb(), 'examples': qube_966b5e661c.sparta_e3b4090eec()}, 'screener': {'input': get_tv_input
        ('screener'), 'options': qube_ebbb432987.sparta_53e08ec931(), 'examples':
        qube_966b5e661c.sparta_d771d1ddd4()}, 'stockAnalysis': {'input':
        get_tv_input('stockAnalysis'), 'options': qube_ebbb432987.sparta_31cfc8d631(), 'examples': qube_966b5e661c.sparta_e3b4090eec('stockAnalysis')}, 'technicalAnalysis':
        {'input': get_tv_input('technicalAnalysis'), 'options':
        qube_ebbb432987.sparta_0c3ac24ef4(), 'examples':
        qube_966b5e661c.sparta_7e9f45c1fa()},
        'companyProfile': {'input': get_tv_input('companyProfile'),
        'options': qube_ebbb432987.sparta_99e39c7898(), 'examples':
        qube_966b5e661c.sparta_e3b4090eec('companyProfile')},
        'topStories': {'input': get_tv_input('topStories'), 'options':
        qube_ebbb432987.sparta_d77fcd7d2c(), 'examples': qube_966b5e661c.sparta_1112c80303()}, 'symbolOverview': {'input':
        get_tv_input('symbolOverview'), 'options': qube_ebbb432987.sparta_9b3bcd4873(), 'examples': qube_966b5e661c.sparta_eaf8b0f225()}, 'symbolMini': {'input':
        get_tv_input('symbolMini'), 'options': qube_ebbb432987.sparta_2f347beff0(), 'examples': qube_966b5e661c.sparta_e3b4090eec('symbolMini')}, 'symbolInfo': {'input':
        get_tv_input('symbolInfo'), 'options': qube_ebbb432987.sparta_33d29d8f3e(), 'examples': qube_966b5e661c.sparta_e3b4090eec('symbolInfo')}, 'singleTicker': {
        'input': get_tv_input('singleTicker'), 'options': qube_ebbb432987.sparta_395796e8db(), 'examples': qube_966b5e661c.sparta_e3b4090eec('singleTicker')}, 'tickerTape': {
        'input': get_tv_input('tickerTape'), 'options': qube_ebbb432987.sparta_4a73f5ac4d(), 'examples': qube_966b5e661c.sparta_2e048f0642()}, 'tickerWidget': {'input': get_tv_input
        ('tickerWidget'), 'options': qube_ebbb432987.sparta_a97dd5c9c5(),
        'examples': qube_966b5e661c.sparta_30bf7df98d()},
        'candlestick': {'input': get_lightweight_input('candlestick'),
        'options': None, 'examples': qube_0014fd4204.sparta_7a3288947c()}, 'ts_line': {'input':
        get_lightweight_input('ts_line'), 'options': None, 'examples':
        qube_0014fd4204.sparta_19c296e218()}, 'ts_area': {'input':
        get_lightweight_input('ts_area'), 'options': None, 'examples':
        qube_0014fd4204.sparta_163910df01()}, 'ts_baseline': {'input':
        get_lightweight_input('ts_baseline'), 'options': None, 'examples':
        qube_0014fd4204.sparta_16cb32dce7()}, 'ts_bar': {'input':
        get_lightweight_input('ts_bar'), 'options': None, 'examples':
        qube_0014fd4204.sparta_365862ed15()}, 'ts_shaded': {'input':
        get_lightweight_input('ts_shaded'), 'options': None, 'examples':
        qube_0014fd4204.sparta_041b1c07ba()}, 'ts_lollipop': {
        'input': get_lightweight_input('ts_lollipop'), 'options': None,
        'examples': qube_0014fd4204.sparta_7b493b383c()}, 'performance':
        {'input': get_lightweight_input('performance'), 'options': None,
        'examples': qube_0014fd4204.sparta_51824adacb()},
        'ts_area_bands': {'input': get_lightweight_input('ts_area_bands'),
        'options': None, 'examples': qube_0014fd4204.sparta_4c44a256b9
        ()}, 'gauge1': {'input': get_gauge_input('gauge1'), 'options':
        qube_c26c31eb40.sparta_5543301330(), 'examples': qube_ace1d6e9fa.sparta_4230fc5911()}, 'gauge2': {'input': get_gauge_input(
        'gauge2'), 'options': qube_c26c31eb40.sparta_6e7fe584a8(), 'examples':
        qube_ace1d6e9fa.sparta_2f1358810f()}, 'gauge3': {'input':
        get_gauge_input('gauge3'), 'options': qube_c26c31eb40.sparta_b449ac7f44(), 'examples': qube_ace1d6e9fa.sparta_aca159b9a9(
        )}, 'gauge4': {'input': get_gauge_input('gauge4'), 'options':
        qube_c26c31eb40.sparta_c224f94e02(), 'examples': qube_ace1d6e9fa.sparta_e8e8d007da()}, 'dataframe': {'input': dataframe_dict,
        'options': None, 'examples': qube_59b2cfc87f.sparta_7b2ac491ad
        ()}, 'quantstats': {'input': quantstats_dict, 'options': None,
        'examples': qube_59b2cfc87f.sparta_17556a8d6a()},
        'dynamicRescale': {'input': dynamic_rescale_dict, 'options': None,
        'examples': qube_2cc46dbb53.sparta_cd1c7dbefa()},
        'regression': {'input': regression_dict, 'options': None,
        'examples': qube_2cc46dbb53.sparta_f4973b2c71()}, 'calendar':
        {'input': calendar_dict, 'options': None, 'examples':
        qube_2cc46dbb53.sparta_ab1cbefda4()}, 'wordcloud': {'input':
        wordcloud_dict, 'options': None, 'examples': qube_2cc46dbb53.sparta_f090a7e0a8()}, 'notebook': {'input': notebook_dict,
        'options': None, 'examples': qube_59b2cfc87f.sparta_8c3cb24da7(
        )}, 'summary_statistics': {'input': summary_statistics_dict,
        'options': None, 'examples': qube_59b2cfc87f.sparta_30bbc0dea1()}, 'OLS': {'input':
        get_df_relationships_default('OLS'), 'options': None, 'examples':
        qube_61bde0b72f.sparta_511f5ad3ee()}, 'PolynomialRegression':
        {'input': get_df_relationships_default('PolynomialRegression'),
        'options': None, 'examples': qube_61bde0b72f.sparta_59f71ec7f7()}, 'DecisionTreeRegression': {'input':
        get_df_relationships_default('DecisionTreeRegression'), 'options':
        None, 'examples': qube_61bde0b72f.sparta_c3797f799c()},
        'RandomForestRegression': {'input': get_df_relationships_default(
        'RandomForestRegression'), 'options': None, 'examples':
        qube_61bde0b72f.sparta_0ba8de97bc()}, 'clustering': {
        'input': get_df_relationships_default('clustering'), 'options':
        None, 'examples': qube_61bde0b72f.sparta_161810e586()},
        'correlation_network': {'input': get_df_relationships_default(
        'correlation_network'), 'options': None, 'examples':
        qube_61bde0b72f.sparta_7cb6d71f04()}, 'pca': {
        'input': get_df_relationships_default('pca'), 'options': None,
        'examples': qube_61bde0b72f.sparta_25981d1370()}, 'tsne': {'input':
        get_df_relationships_default('tsne'), 'options': None, 'examples':
        qube_61bde0b72f.sparta_156d032dae()}, 'features_importance': {
        'input': get_df_relationships_default('features_importance'),
        'options': None, 'examples': qube_61bde0b72f.sparta_3a4a8cac14()}, 'mutual_information': {'input':
        get_df_relationships_default('mutual_information'), 'options': None,
        'examples': qube_61bde0b72f.sparta_d7e30eaf8c()},
        'quantile_regression': {'input': get_df_relationships_default(
        'quantile_regression'), 'options': None, 'examples':
        qube_61bde0b72f.sparta_58804447ed()},
        'rolling_regression': {'input': get_df_relationships_default(
        'rolling_regression'), 'options': None, 'examples': qube_61bde0b72f.sparta_ee4ee113cb()}, 'recursive_regression': {
        'input': get_df_relationships_default('recursive_regression'),
        'options': None, 'examples': qube_61bde0b72f.sparta_dadf2d66f1()}, 'stl': {'input':
        get_df_tsa_default('stl'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_7ad6fd2d08()}, 'wavelet': {'input':
        get_df_tsa_default('wavelet'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_ad14647749()}, 'hmm': {'input':
        get_df_tsa_default('hmm'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_a048093214()}, 'cusum': {'input':
        get_df_tsa_default('cusum'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_f64ba8a89f()}, 'ruptures': {'input':
        get_df_tsa_default('ruptures'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_e8f82e86fd()}, 'zscore': {'input':
        get_df_tsa_default('zscore'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_2b24b09299()}, 'prophet_outlier': {'input':
        get_df_tsa_default('prophet_outlier'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_d2536ed059()}, 'isolation_forest':
        {'input': get_df_tsa_default('isolation_forest'), 'options': None,
        'examples': qube_60bc8c5499.sparta_a4543134e1()}, 'mad':
        {'input': get_df_tsa_default('mad'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_3de17cdcb1()}, 'sarima': {'input':
        get_df_tsa_default('sarima'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_5925fdf5c5()}, 'ets': {'input':
        get_df_tsa_default('ets'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_75008f93f2()}, 'prophet_forecast': {'input':
        get_df_tsa_default('prophet_forecast'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_8182239958()}, 'var': {'input':
        get_df_tsa_default('var'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_2723340d8d()}, 'adf_test': {'input':
        get_df_tsa_default('adf_test'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_aad7f9d40d()}, 'kpss_test': {'input':
        get_df_tsa_default('kpss_test'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_f4e9ad1f80()}, 'perron_test': {'input':
        get_df_tsa_default('perron_test'), 'options': None, 'examples':
        qube_60bc8c5499.sparta_8f81b788f8()}, 'zivot_andrews_test':
        {'input': get_df_tsa_default('zivot_andrews_test'), 'options': None,
        'examples': qube_60bc8c5499.sparta_7fc74fbb8c()},
        'granger_test': {'input': get_df_tsa_default('granger_test'),
        'options': None, 'examples': qube_60bc8c5499.sparta_f6ad3b9e0d()}, 'cointegration_test': {'input':
        get_df_tsa_default('cointegration_test'), 'options': None,
        'examples': qube_60bc8c5499.sparta_48fb2271b2()},
        'canonical_corr': {'input': get_df_tsa_default('canonical_corr'),
        'options': None, 'examples': qube_60bc8c5499.sparta_62c844f609()}}
    return inputs_options


def sparta_bde78f492a(plot_type: str='line') ->dict:
    plot_types_list = sparta_b770ba5f34()
    try:
        plot_dict = [elem for elem in plot_types_list if elem['ID'] ==
            plot_type][0]
        plot_library = plot_dict['Library']
        plot_name = plot_dict['Name']
    except:
        plot_library = ''
        plot_name = plot_type.capitalize()
    plot_inputs_options_dict = sparta_02318b41b3()[plot_type]
    plot_inputs_options_dict['plot_name'] = plot_name
    plot_inputs_options_dict['plot_library'] = plot_library
    return plot_inputs_options_dict

#END OF QUBE
