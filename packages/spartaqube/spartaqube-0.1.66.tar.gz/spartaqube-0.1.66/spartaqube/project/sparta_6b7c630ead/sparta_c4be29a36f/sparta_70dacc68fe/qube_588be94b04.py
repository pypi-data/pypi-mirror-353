import json
from django.conf import settings as conf_settings


def sparta_a049a6ae10(type='line') ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    tooltip_title_options = 'f"title-{round(price,2)}"'
    tooltip_label_options = 'f"label-{round(price,2)}"'
    return [{'title': f'Simple {type}', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Two {type}s with legend', 'description':
        'Example to plot a two time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  legend=['High', 'Low'], 
  height=500
)
plot_example"""
        }, {'title': f'Two stacked {type}s', 'description':
        'Example to plot a two time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  stacked=True,
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with title', 'description':
        'Example to plot a simple time series with custom title using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  title='Apple Close Prices', 
  title_css={json.dumps(title_css_dict)},
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with datalabels', 'description':
        'Example to plot a simple time series with datalabels using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  datalabels=apple_price_df['Close'],
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with conditional colors',
        'description': 'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
apple_price_df['vol_colors'] = 'red'
apple_price_df.loc[apple_price_df['Volume'] > apple_price_df['Volume'].mean(), 'vol_colors'] = 'green'
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  border=apple_price_df['vol_colors'].tolist(), 
  background=apple_price_df['vol_colors'],
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with tooltips', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  tooltips_title=[{tooltip_title_options} for price in apple_price_df['Close'].tolist()],
  tooltips_label=[{tooltip_label_options} for price in apple_price_df['Close'].tolist()],
  labels=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with date formatting', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description':
        'year: y, month: M, day: d, quarter: QQQ, week: w, hour: HH, minute: MM, seconds: SS, millisecond: ms'
        , 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  date_format='yyyy-MM-dd',
  labels=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with time range', 'description':
        f'Example to plot a simple {type} chart with lightweight chart',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example {type}',
  time_range=True,
  height=500
)
plot_example"""
        }]


def sparta_9a4308f6f6() ->list:
    return sparta_a049a6ae10(type='line')


def sparta_3ab50def6c() ->list:
    return sparta_a049a6ae10(type='bar')


def sparta_577b615514() ->list:
    return sparta_a049a6ae10(type='scatter')


def sparta_7e54e11f33() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'area'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    tooltip_title_options = 'f"title-{round(price,2)}"'
    tooltip_label_options = 'f"label-{round(price,2)}"'
    return [{'title': f'Simple {type}', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Two {type}s with legend', 'description':
        'Example to plot a two time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  legend=['High', 'Low'], 
  height=500
)
plot_example"""
        }, {'title': f'Two stacked {type}s', 'description':
        'Example to plot a two time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  stacked=True,
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with title', 'description':
        'Example to plot a simple time series with custom title using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  title='Apple Close Prices', 
  title_css={json.dumps(title_css_dict)},
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with datalabels', 'description':
        'Example to plot a simple time series with datalabels using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  datalabels=apple_price_df['Close'],
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with tooltips', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  tooltips_title=[{tooltip_title_options} for price in apple_price_df['Close'].tolist()],
  tooltips_label=[{tooltip_label_options} for price in apple_price_df['Close'].tolist()],
  labels=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with date formatting', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description':
        'year: y, month: M, day: d, quarter: QQQ, week: w, hour: HH, minute: MM, seconds: SS, millisecond: ms'
        , 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  date_format='yyyy-MM-dd',
  labels=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with time range', 'description':
        f'Example to plot a simple {type} chart with lightweight chart',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example {type}',
  time_range=True,
  height=500
)
plot_example"""
        }]


def sparta_999f59d5a5(type='pie') ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    options_datalabels = """{
    "datasets": [
        {
            "datalabels": {
                "display": True,
                "color": "red",
                "font": {
                    "family": "Azonix",
                    "size": 20,
                }
            },
        }
    ]
  }"""
    options_datasets_colors = """{
    "datasets": [
        {
            "backgroundColor": ['red', 'blue', 'green'],
            "borderColor": ['red', 'blue', 'green'],
        }
    ]
  }"""
    return [{'title': f'Simple {type}', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=[1,2,3], 
  y=[20,60,20], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with labels', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=[1,2,3], 
  y=[20,60,20],
  datalabels=['group 1', 'group 2', 'group 3'],
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with custom labels', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=[1,2,3], 
  y=[20,60,20],
  options={options_datalabels},
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with custom colors', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=[1,2,3], 
  y=[20,60,20],
  options={options_datasets_colors},
  height=500
)
plot_example"""
        }]


def sparta_08b6dd8bf1() ->list:
    return sparta_999f59d5a5(type='donut')


def sparta_83f52c96b7() ->list:
    return sparta_999f59d5a5(type='polar')


def sparta_a76181a12e() ->list:
    """
    
    """
    type = 'bubble'
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    tooltip_title_options = 'f"title-{round(price,2)}"'
    tooltip_label_options = 'f"label-{round(price,2)}"'
    return [{'title': f'Simple {type}', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with radius', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  r=apple_price_df['Volume'], 
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Two {type}s with legend', 'description':
        'Example to plot a two time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  legend=['High', 'Low'], 
  height=500
)
plot_example"""
        }, {'title': f'Two stacked {type}s', 'description':
        'Example to plot a two time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  stacked=True,
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with title', 'description':
        'Example to plot a simple time series with custom title using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  title='Apple Close Prices', 
  title_css={json.dumps(title_css_dict)},
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with datalabels', 'description':
        'Example to plot a simple time series with datalabels using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  datalabels=apple_price_df['Close'],
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with conditional colors',
        'description': 'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
apple_price_df['vol_colors'] = 'red'
apple_price_df.loc[apple_price_df['Volume'] > apple_price_df['Volume'].mean(), 'vol_colors'] = 'green'
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  r=apple_price_df['Volume'], 
  border=apple_price_df['vol_colors'].tolist(), 
  background=apple_price_df['vol_colors'],
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with tooltips', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  r=apple_price_df['Volume'], 
  tooltips_title=[{tooltip_title_options} for price in apple_price_df['Close'].tolist()],
  tooltips_label=[{tooltip_label_options} for price in apple_price_df['Close'].tolist()],
  labels=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with date formatting', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description':
        'year: y, month: M, day: d, quarter: QQQ, week: w, hour: HH, minute: MM, seconds: SS, millisecond: ms'
        , 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  r=apple_price_df['Volume'], 
  date_format='yyyy-MM-dd',
  labels=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with time range', 'description':
        f'Example to plot a simple {type} chart with lightweight chart',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  r=apple_price_df['Volume'], 
  title='Example {type}',
  time_range=True,
  height=500
)
plot_example"""
        }]


def sparta_5e6988cc50() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    tooltip_title_options = 'f"title-{round(price,2)}"'
    tooltip_label_options = 'f"label-{round(price,2)}"'
    type = 'barH'
    return [{'title': f'Simple horizontal bar', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Two horizontal bars with legend', 'description':
        'Example to plot a two time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  legend=['High', 'Low'], 
  height=500
)
plot_example"""
        }, {'title': f'Two stacked horizontal bars', 'description':
        'Example to plot a two time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  stacked=True,
  height=500
)
plot_example"""
        }, {'title': f'Simple horizontal bar with title', 'description':
        'Example to plot a simple time series with custom title using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  title='Apple Close Prices', 
  title_css={json.dumps(title_css_dict)},
  height=500
)
plot_example"""
        }, {'title': f'Simple horizontal bar with datalabels',
        'description':
        'Example to plot a simple time series with datalabels using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  datalabels=apple_price_df['Close'],
  legend=['AAPL'], 
  height=500
)
plot_example"""
        }, {'title': f'Simple horizontal bar with tooltips', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  tooltips_title=[{tooltip_title_options} for price in apple_price_df['Close'].tolist()],
  tooltips_label=[{tooltip_label_options} for price in apple_price_df['Close'].tolist()],
  labels=['AAPL'], 
  height=500
)
plot_example"""
        }]


def sparta_dfcf8a36ef() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'radar'
    title_css_dict = {'color': 'blue', 'text-align': 'center', 'font-size':
        '12px'}
    tooltip_title_options = 'f"title-{round(price,2)}"'
    tooltip_label_options = 'f"label-{round(price,2)}"'
    options_tension = """{
    "datasets": [
        {
            "tension": 0
        }
    ]
  }"""
    return [{'title': f'Simple {type}', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=["A", "B", "C", "D", "E", "F", "G"], 
  y=[65, 59, 90, 81, 56, 55, 40], 
  height=500
)
plot_example"""
        }, {'title': f'Simple {type} with custom tension', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=["A", "B", "C", "D", "E", "F", "G"], 
  y=[65, 59, 90, 81, 56, 55, 40], 
  options={options_tension},
  height=500
)
plot_example"""
        }]


def sparta_b1b58a8051() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'mixed'
    options_mixed = """{
    "datasets": [
        {
            "type": 'bar',
        },
        {
            "type": 'line',
        }
    ]
  }"""
    return [{'title': f'Simple {type}', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=[apple_price_df['Close'], apple_price_df['High']], 
  option={options_mixed}, 
  height=500
)
plot_example"""
        }]


def sparta_1545b34ec3() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'histogram'
    return [{'title': f'Simple {type}', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
apple_ret_df = apple_price_df[['Close']].pct_change().dropna()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  y=apple_ret_df['Close'], 
  height=500
)
plot_example"""
        }]


def sparta_38bf5c9203() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'matrix'
    data_matrix = (
        "{'AAPL': apple_ret_df['Close'], 'NVDA': nvda_ret_df['Close'], 'TSLA': tsla_ret_df['Close']}"
        )
    gradient_color = """{
    'options': {
        "gradientColors": {
            "bGradientMatrix": True,
            "gradientStart": "#20ff86ff",
            "gradientMiddle": "#f8e61cff",
            "gradientEnd": "#ff0000ff",
            "gradientFixedBorderColor": False,
            "gradientBorderColor": "#ffffffff",
            "gradientBorderWidth": 1,
            "bDisplayHeatbar": True,
            "heatBarPosition": "Right",
            "bMiddleColor": True,
        },
    }
  }"""
    return [{'title': f'Simple {type}', 'description':
        'Example to plot a simple time series using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
apple_ret_df = apple_price_df.pct_change().iloc[-10:]
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_ret_df.index, 
  y=apple_ret_df['Close'],
  date_format='yyyy-MM-dd',
  height=500
)
plot_example"""
        }, {'title': f'Correlation matrix example', 'description':
        'Example to plot a simple correlation matrix using chartJS',
        'sub_description': '', 'code':
        f"""{import_module}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
apple_ret_df = apple_price_df.pct_change()
nvda_price_df = yf.Ticker("NVDA").history(period="1y")
nvda_ret_df = nvda_price_df.pct_change()
tsla_price_df = yf.Ticker("TSLA").history(period="1y")
tsla_ret_df = tsla_price_df.pct_change()
df = pd.DataFrame({data_matrix})
# Compute the correlation matrix
correlation_matrix = df.corr()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=correlation_matrix.index, 
  y=[correlation_matrix['AAPL'], correlation_matrix['NVDA'], correlation_matrix['TSLA']],
  options={gradient_color},
  height=500
)
plot_example"""
        }]

#END OF QUBE
