import json
from django.conf import settings as conf_settings


def sparta_e3b4090eec(type='realTimeStock') ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    options_symbol = "{'symbol': 'NASDAQ:NVDA'}"
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a real time stock using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom symbol',
        'description':
        'Example to display a real time stock using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_symbol},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_42c4f3e28b() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'stockHeatmap'
    options_datasource = "{'dataSource': 'DAX'}"
    options_metrics = "{'blockColor': 'Perf.YTD'}"
    options_heatmap_size = "{'blockSize': 'volume|1W'}"
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a stock heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'YTD performance heatmap', 'description':
        'Example to display a stock heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_metrics},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom heatmap size',
        'description':
        'Example to display a stock heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_heatmap_size},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom data source',
        'description':
        'Example to display a stock heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_datasource},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_1404bac267() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'economicCalendar'
    options_countries = "{'countryFilter': 'us, eu, il'}"
    return [{'title': f'Economic calendar', 'description':
        'Example to display an economic calendar using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'],
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'Economic calendar with custom countries',
        'description':
        'Example to display an economic calendar using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_countries},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_f91b062026() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'etfHeatmap'
    options_datasource = "{'dataSource': 'AllCHEEtf'}"
    options_metrics = "{'blockColor': 'Perf.YTD'}"
    options_heatmap_size = "{'blockSize': 'volume|1M'}"
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a etf heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'YTD performance heatmap', 'description':
        'Example to display a etf heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_metrics},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom heatmap size',
        'description': 'Example to display a etf heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_heatmap_size},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom data source',
        'description': 'Example to display a etf heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_datasource},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_2010ef85e6() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'cryptoTable'
    options_performance = "{'defaultColumn': 'performance'}"
    options_oscillators = "{'defaultColumn': 'oscillators'}"
    options_moving_average = "{'defaultColumn': 'moving_averages'}"
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a crypto table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with performance data source',
        'description':
        'Example to display a crypto table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_performance},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with oscillator data',
        'description':
        'Example to display a crypto table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_oscillators},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with moving average data',
        'description':
        'Example to display a crypto table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_moving_average},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_f64db7e561() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'cryptoHeatmap'
    options_metrics = "{'blockColor': 'Perf.YTD'}"
    options_heatmap_size = "{'blockSize': 'volume|1W'}"
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a crypto heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'YTD performance heatmap', 'description':
        'Example to display a crypto heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_metrics},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom heatmap size',
        'description':
        'Example to display a crypto heatmap using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_heatmap_size},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_dfec8591b7(type='forex') ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    options_countries = "{'currencies': ['USD', 'EUR', 'CHF', 'GBP', 'JPY']}"
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a forex live table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom currencies',
        'description':
        'Example to display a forex live table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_countries},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_5e76fe802c() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    options_data = """{
        "symbolsGroups": [
            {
                "name": "Indices",
                "originalName": "Indices",
                "symbols": [
                    {
                        "name": "FOREXCOM:SPXUSD",
                        "displayName": "S&P 500",
                    },
                    {
                        "name": "FOREXCOM:NSXUSD",
                        "displayName": "US 100",
                    },
                ],
            },
            {
                "name": "Futures",
                "originalName": "Futures",
                "symbols": [
                    {
                        "name": "CME_MINI:ES1!",
                        "displayName": "S&P 500",
                    },
                    {
                        "name": "CME:6E1!",
                        "displayName": "Euro",
                    },
                ],
            },
            {
                "name": "Bonds",
                "originalName": "Bonds",
                "symbols": [
                    {
                        "name": "CBOT:ZB1!",
                        "displayName": "T-Bond",
                    },
                    {
                        "name": "CBOT:UB1!",
                        "displayName": "Ultra T-Bond",
                    },
                ],
            },
            {
                "name": "Forex",
                "originalName": "Forex",
                "symbols": [
                    {
                        "name": "FX:EURUSD",
                        "displayName": "EUR to USD",
                    },
                    {
                        "name": "FX:GBPUSD",
                        "displayName": "GBP to USD",
                    },
                ],
            },
        ]
    }"""
    type = 'marketData'
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a market data table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom data', 'description':
        'Example to display a market data table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_data},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_d771d1ddd4() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'screener'
    options_performance = "{'defaultColumn': 'performance'}"
    options_oscillators = "{'defaultColumn': 'oscillators'}"
    options_moving_average = "{'defaultColumn': 'moving_averages'}"
    rising_pairs = "{'defaultScreen': 'top_gainers'}"
    market = "{'market': 'switzerland'}"
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a screener table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with performance data source',
        'description':
        'Example to display a screener table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_performance},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with oscillator data',
        'description':
        'Example to display a screener table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_oscillators},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with moving average data',
        'description':
        'Example to display a screener table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_moving_average},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} for rising pairs', 'description':
        'Example to display a screener table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={rising_pairs},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} for custom market',
        'description':
        'Example to display a screener table using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={market},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_7e9f45c1fa() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'technicalAnalysis'
    options_symbol = "{'symbol': 'NASDAQ:NVDA'}"
    options_interval = "{'interval': '1h'}"
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a technical indicator chart using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom symbol',
        'description':
        'Example to display a technical indicator chart using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_symbol},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title':
        f'{type.capitalize()} with custom interval (last hour)',
        'description':
        'Example to display a technical indicator chart using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_interval},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_1112c80303() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'topStories'
    options_symbol = "{'symbol': 'NASDAQ:NVDA'}"
    options_crypto = "{'feedMode': 'market', 'market': 'crypto'}"
    options_stock = "{'feedMode': 'market', 'market': 'stock'}"
    options_indices = "{'feedMode': 'market', 'market': 'index'}"
    return [{'title': f'{type.capitalize()} (all symbols)', 'description':
        'Example to display a technical indicator chart using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} custom symbol', 'description':
        'Example to display a technical indicator chart using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_symbol},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} for cryptocurrencies',
        'description':
        'Example to display a technical indicator chart using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_crypto},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} for stocks', 'description':
        'Example to display a technical indicator chart using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_stock},
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} for indices', 'description':
        'Example to display a technical indicator chart using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_indices},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_eaf8b0f225() ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    type = 'symbolOverview'
    options_symbol = "{'symbol': 'NASDAQ:NVDA'}"
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a symbol overview using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom symbol',
        'description':
        'Example to display a symbol overview using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_symbol},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_2e048f0642(type='tickerTape') ->list:
    """
    
    """
    import_module = 'from spartaqube import Spartaqube as Spartaqube'
    options_symbol = """{
        "symbols": [
            {
                "proName": "FOREXCOM:SPXUSD",
			    "title": "S&P 500",
            },
            {
                "proName": "FOREXCOM:NSXUSD",
			    "title": "US 100",
            },
        ]
}"""
    return [{'title': f'{type.capitalize()}', 'description':
        'Example to display a ticker tape using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  interactive=False,
  height=500
)
plot_example"""
        }, {'title': f'{type.capitalize()} with custom symbols',
        'description': 'Example to display a ticker tape using TradingView',
        'sub_description': '', 'code':
        f"""{import_module}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  options={options_symbol},
  interactive=False,
  height=500
)
plot_example"""
        }]


def sparta_30bf7df98d() ->list:
    """
    
    """
    return sparta_2e048f0642('tickerWidget')

#END OF QUBE
