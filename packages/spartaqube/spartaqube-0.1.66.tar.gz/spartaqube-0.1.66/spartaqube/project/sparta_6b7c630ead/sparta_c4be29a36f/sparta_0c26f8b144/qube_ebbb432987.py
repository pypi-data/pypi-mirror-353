def sparta_0669b53e6d() ->dict:
    """
    Real Time Stock
    """
    return {'autosize': {'doc_description':
        'Automatically size the widget to fit its container', 'doc_type':
        'Boolean', 'doc_default': True}, 'symbol': {'doc_description':
        'The symbol of the financial instrument to display (e.g., NASDAQ:AAPL)'
        , 'doc_type': 'String', 'doc_default': 'NASDAQ:AAPL'}, 'interval':
        {'doc_description':
        'The interval of the chart (e.g., "D" for daily, "W" for weekly)',
        'doc_type': 'String', 'doc_default': 'D'}, 'timezone': {
        'doc_description':
        'The timezone for the chart (e.g., "Etc/UTC", "America/New_York")',
        'doc_type': 'String', 'doc_default': 'Etc/UTC'}, 'theme': {
        'doc_description': 'The theme of the chart (e.g., "light", "dark")',
        'doc_type': 'String', 'doc_default': 'light'}, 'style': {
        'doc_description':
        'The style of the chart (e.g., "1" for candles, "2" for bars)',
        'doc_type': 'String', 'doc_default': '1'}, 'locale': {
        'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}, 'enable_publishing':
        {'doc_description':
        'Enable or disable the option to publish charts', 'doc_type':
        'Boolean', 'doc_default': False}, 'allow_symbol_change': {
        'doc_description':
        'Allow or disallow the ability to change the symbol in the widget',
        'doc_type': 'Boolean', 'doc_default': True}}


def sparta_1107e3a1c1() ->dict:
    """
    Stock Heatmap
    """
    return {'exchanges': {'doc_description':
        'List of exchanges to display data from', 'doc_type': 'Array',
        'doc_default': []}, 'dataSource': {'doc_description':
        'The data source for the widget, typically an index symbol like SPX500'
        , 'doc_type': 'String', 'doc_default': 'SPX500'}, 'grouping': {
        'doc_description': 'Grouping of the data in the widget', 'doc_type':
        'String', 'doc_default': 'sector'}, 'blockSize': {'doc_description':
        'Size of the block for data representation', 'doc_type': 'String',
        'doc_default': 'market_cap_basic'}, 'blockColor': {
        'doc_description': 'Color of the block for data representation',
        'doc_type': 'String', 'doc_default': 'change'}, 'locale': {
        'doc_description': 'The language of the widget interface',
        'doc_type': 'String', 'doc_default': 'en'}, 'symbolUrl': {
        'doc_description': 'URL for the symbol used in the widget',
        'doc_type': 'String', 'doc_default': ''}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'hasTopBar': {'doc_description':
        'Whether the widget has a top bar', 'doc_type': 'Boolean',
        'doc_default': False}, 'isDataSetEnabled': {'doc_description':
        'Enable or disable the data set', 'doc_type': 'Boolean',
        'doc_default': False}, 'isZoomEnabled': {'doc_description':
        'Enable or disable zoom functionality', 'doc_type': 'Boolean',
        'doc_default': True}, 'hasSymbolTooltip': {'doc_description':
        'Display tooltips for symbols', 'doc_type': 'Boolean',
        'doc_default': True}, 'width': {'doc_description':
        'Width of the widget', 'doc_type': 'String', 'doc_default': '100%'},
        'height': {'doc_description': 'Height of the widget', 'doc_type':
        'String', 'doc_default': '100%'}}


def sparta_9bdd5b6d04() ->dict:
    """
    Economic calendar
    """
    return {'colorTheme': {'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'isTransparent': {
        'doc_description': 'Whether the widget background is transparent',
        'doc_type': 'Boolean', 'doc_default': False}, 'width': {
        'doc_description': 'Width of the widget', 'doc_type': 'String',
        'doc_default': '100%'}, 'height': {'doc_description':
        'Height of the widget', 'doc_type': 'String', 'doc_default': '100%'
        }, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English)',
        'doc_type': 'String', 'doc_default': 'en'}, 'importanceFilter': {
        'doc_description':
        'Filter events by importance (e.g., "-1,0,1" for low, medium, high)',
        'doc_type': 'String', 'doc_default': '-1,0,1'}, 'countryFilter': {
        'doc_description':
        'Filter events by country (e.g., "us,eu,it,nz,ch,au,fr,jp,za,tr,ca,de,mx,es,gb")'
        , 'doc_type': 'String', 'doc_default':
        'us,eu,it,nz,ch,au,fr,jp,za,tr,ca,de,mx,es,gb'}}


def sparta_d2d8f7ef79() ->dict:
    """
    Economic Calendar
    """
    return {'width': {'doc_description': 'Width of the widget', 'doc_type':
        'String', 'doc_default': '100%'}, 'height': {'doc_description':
        'Height of the widget', 'doc_type': 'String', 'doc_default': '100%'
        }, 'defaultColumn': {'doc_description':
        'The default column to display in the screener (e.g., "overview", "performance")'
        , 'doc_type': 'String', 'doc_default': 'overview'}, 'screener_type':
        {'doc_description':
        'The type of screener to use (e.g., "crypto_mkt" for cryptocurrency market)'
        , 'doc_type': 'String', 'doc_default': 'crypto_mkt'},
        'displayCurrency': {'doc_description':
        'The currency in which to display values (e.g., "USD", "EUR")',
        'doc_type': 'String', 'doc_default': 'USD'}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English)',
        'doc_type': 'String', 'doc_default': 'en'}}


def sparta_f203138950() ->dict:
    """
    Stock Heatmap
    """
    return {'dataSource': {'doc_description':
        'The source of the data used in the widget', 'doc_type': 'String',
        'doc_default': ''}, 'blockSize': {'doc_description':
        'Size of the block for data representation', 'doc_type': 'String',
        'doc_default': ''}, 'blockColor': {'doc_description':
        'Color of the block for data representation', 'doc_type': 'String',
        'doc_default': ''}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English)',
        'doc_type': 'String', 'doc_default': 'en'}, 'symbolUrl': {
        'doc_description': 'URL for the symbol used in the widget',
        'doc_type': 'String', 'doc_default': ''}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'hasTopBar': {'doc_description':
        'Whether the widget has a top bar', 'doc_type': 'Boolean',
        'doc_default': False}, 'isDataSetEnabled': {'doc_description':
        'Enable or disable the data set', 'doc_type': 'Boolean',
        'doc_default': False}, 'isZoomEnabled': {'doc_description':
        'Enable or disable zoom functionality', 'doc_type': 'Boolean',
        'doc_default': True}, 'hasSymbolTooltip': {'doc_description':
        'Display tooltips for symbols', 'doc_type': 'Boolean',
        'doc_default': True}, 'width': {'doc_description':
        'Width of the widget', 'doc_type': 'String', 'doc_default': '100%'},
        'height': {'doc_description': 'Height of the widget', 'doc_type':
        'String', 'doc_default': '100%'}}


def sparta_673f175814() ->dict:
    """
    Stock Heatmap
    """
    return {'width': {'doc_description': 'Width of the widget', 'doc_type':
        'String', 'doc_default': '100%'}, 'height': {'doc_description':
        'Height of the widget', 'doc_type': 'String', 'doc_default': '100%'
        }, 'currencies': {'doc_description':
        'List of currencies to display in the widget', 'doc_type': 'List',
        'doc_default':
        "['EUR', 'USD', 'JPY', 'GBP', 'CHF', 'AUD', 'CAD', 'NZD']"},
        'isTransparent': {'doc_description':
        'Whether the widget background is transparent', 'doc_type':
        'Boolean', 'doc_default': False}, 'colorTheme': {'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}}


def sparta_fa9de7f4d9() ->dict:
    """
    Stock Heatmap
    """
    return {'width': {'doc_description': 'Width of the widget', 'doc_type':
        'String', 'doc_default': '100%'}, 'height': {'doc_description':
        'Height of the widget', 'doc_type': 'String', 'doc_default': '100%'
        }, 'currencies': {'doc_description':
        'List of currencies to display in the widget', 'doc_type': 'List',
        'doc_default':
        "['EUR', 'USD', 'JPY', 'GBP', 'CHF', 'AUD', 'CAD', 'NZD']"},
        'isTransparent': {'doc_description':
        'Whether the widget background is transparent', 'doc_type':
        'Boolean', 'doc_default': False}, 'colorTheme': {'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}}


def sparta_7dd5028b04() ->dict:
    """
    Stock Heatmap
    """
    return {'width': {'doc_description': 'Width of the widget', 'doc_type':
        'String', 'doc_default': '100%'}, 'height': {'doc_description':
        'Height of the widget', 'doc_type': 'String', 'doc_default': '100%'
        }, 'symbolsGroups': {'doc_description':
        'List of symbols to display', 'doc_type': 'list', 'doc_default':
        """
[
    {
        "name": "Indices",
        "originalName": "Indices",
        "symbols": [
            {
            "name": "FOREXCOM:SPXUSD",
            "displayName": "S&P 500"
            },
            {
            "name": "FOREXCOM:NSXUSD",
            "displayName": "US 100"
            },
            {
            "name": "FOREXCOM:DJI",
            "displayName": "Dow 30"
            },
            {
            "name": "INDEX:NKY",
            "displayName": "Nikkei 225"
            },
            {
            "name": "INDEX:DEU40",
            "displayName": "DAX Index"
            },
            {
            "name": "FOREXCOM:UKXGBP",
            "displayName": "UK 100"
            }
        ]
    },
    {
        "name": "Futures",
        "originalName": "Futures",
        "symbols": [
            {
            "name": "CME_MINI:ES1!",
            "displayName": "S&P 500"
            },
            {
            "name": "CME:6E1!",
            "displayName": "Euro"
            },
            {
            "name": "COMEX:GC1!",
            "displayName": "Gold"
            },
            {
            "name": "NYMEX:CL1!",
            "displayName": "WTI Crude Oil"
            },
            {
            "name": "NYMEX:NG1!",
            "displayName": "Gas"
            },
            {
            "name": "CBOT:ZC1!",
            "displayName": "Corn"
            }
        ]
    },
]
"""
        }, 'showSymbolLogo': {'doc_description': 'Display symbol logo',
        'doc_type': 'Boolean', 'doc_default': True}, 'isTransparent': {
        'doc_description': 'Whether the widget background is transparent',
        'doc_type': 'Boolean', 'doc_default': False}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}}


def sparta_f192d265cb() ->dict:
    """
    Stock Heatmap
    """
    return {'colorTheme': {'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'dateRange': {'doc_description':
        'The date range for the data displayed in the widget (e.g., "1D", "5D", "1M", "3M", "6M", "12M", "YTD", "ALL")'
        , 'doc_type': 'String', 'doc_default': '12M'}, 'exchange': {
        'doc_description':
        'The exchange for the symbol (e.g., "US", "LSE", "HKEX")',
        'doc_type': 'String', 'doc_default': 'US'}, 'showChart': {
        'doc_description': 'Whether to show the chart in the widget',
        'doc_type': 'Boolean', 'doc_default': True}, 'locale': {
        'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}, 'largeChartUrl': {
        'doc_description':
        'URL for displaying a larger version of the chart', 'doc_type':
        'String', 'doc_default': ''}, 'isTransparent': {'doc_description':
        'Whether the widget background is transparent', 'doc_type':
        'Boolean', 'doc_default': False}, 'showSymbolLogo': {
        'doc_description': 'Whether to show the symbol logo in the widget',
        'doc_type': 'Boolean', 'doc_default': False}, 'showFloatingTooltip':
        {'doc_description':
        'Whether to show a floating tooltip on the chart', 'doc_type':
        'Boolean', 'doc_default': False}, 'width': {'doc_description':
        'Width of the widget', 'doc_type': 'String', 'doc_default': '400'},
        'height': {'doc_description': 'Height of the widget', 'doc_type':
        'String', 'doc_default': '600'}, 'plotLineColorGrowing': {
        'doc_description':
        'Color of the plot line when the value is growing', 'doc_type':
        'String', 'doc_default': 'rgba(41, 98, 255, 1)'},
        'plotLineColorFalling': {'doc_description':
        'Color of the plot line when the value is falling', 'doc_type':
        'String', 'doc_default': 'rgba(41, 98, 255, 1)'}, 'gridLineColor':
        {'doc_description': 'Color of the grid lines in the chart',
        'doc_type': 'String', 'doc_default': 'rgba(240, 243, 250, 1)'},
        'scaleFontColor': {'doc_description':
        'Color of the font used for scales in the chart', 'doc_type':
        'String', 'doc_default': 'rgba(106, 109, 120, 1)'},
        'belowLineFillColorGrowing': {'doc_description':
        'Fill color below the line when the value is growing', 'doc_type':
        'String', 'doc_default': 'rgba(41, 98, 255, 0.12)'},
        'belowLineFillColorFalling': {'doc_description':
        'Fill color below the line when the value is falling', 'doc_type':
        'String', 'doc_default': 'rgba(41, 98, 255, 0.12)'},
        'belowLineFillColorGrowingBottom': {'doc_description':
        'Bottom fill color below the line when the value is growing',
        'doc_type': 'String', 'doc_default': 'rgba(41, 98, 255, 0)'},
        'belowLineFillColorFallingBottom': {'doc_description':
        'Bottom fill color below the line when the value is falling',
        'doc_type': 'String', 'doc_default': 'rgba(41, 98, 255, 0)'},
        'symbolActiveColor': {'doc_description':
        'Active color for the symbol', 'doc_type': 'String', 'doc_default':
        'rgba(41, 98, 255, 0.12)'}}


def sparta_53e08ec931() ->dict:
    """
    Stock Heatmap
    """
    return {'width': {'doc_description': 'Width of the widget', 'doc_type':
        'String', 'doc_default': '100%'}, 'height': {'doc_description':
        'Height of the widget', 'doc_type': 'String', 'doc_default': '100%'
        }, 'defaultColumn': {'doc_description':
        'The default column to display in the screener (e.g., "overview", "performance")'
        , 'doc_type': 'String', 'doc_default': 'overview'}, 'defaultScreen':
        {'doc_description':
        'The default screen to display in the screener (e.g., "general", "most_capitalized")'
        , 'doc_type': 'String', 'doc_default': 'general'}, 'market': {
        'doc_description':
        'The market to display in the widget (e.g., "forex", "crypto")',
        'doc_type': 'String', 'doc_default': 'forex'}, 'showToolbar': {
        'doc_description': 'Whether to show the toolbar in the widget',
        'doc_type': 'Boolean', 'doc_default': True}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}}


def sparta_31cfc8d631() ->dict:
    """
    Stock Heatmap
    """
    return {'isTransparent': {'doc_description':
        'Whether the widget background is transparent', 'doc_type':
        'Boolean', 'doc_default': False}, 'largeChartUrl': {
        'doc_description':
        'URL for displaying a larger version of the chart', 'doc_type':
        'String', 'doc_default': ''}, 'displayMode': {'doc_description':
        'The display mode of the widget (e.g., "regular", "compact")',
        'doc_type': 'String', 'doc_default': 'regular'}, 'width': {
        'doc_description': 'Width of the widget', 'doc_type': 'String',
        'doc_default': '400'}, 'height': {'doc_description':
        'Height of the widget', 'doc_type': 'String', 'doc_default': '100%'
        }, 'colorTheme': {'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'symbol': {'doc_description':
        'The symbol of the financial instrument to display (e.g., NASDAQ:AAPL)'
        , 'doc_type': 'String', 'doc_default': 'NASDAQ:AAPL'}, 'locale': {
        'doc_description':
        'The language of the widget interface (e.g., "en" for English)',
        'doc_type': 'String', 'doc_default': 'en'}}


def sparta_0c3ac24ef4() ->dict:
    """
    Stock Heatmap
    """
    return {'interval': {'doc_description':
        'The interval of the chart (e.g., "D" for daily, "W" for weekly)',
        'doc_type': 'String', 'doc_default': 'D'}, 'isTransparent': {
        'doc_description': 'Whether the widget background is transparent',
        'doc_type': 'Boolean', 'doc_default': False}, 'symbol': {
        'doc_description':
        'The symbol of the financial instrument to display (e.g., NASDAQ:AAPL)'
        , 'doc_type': 'String', 'doc_default': 'NASDAQ:AAPL'},
        'showIntervalTabs': {'doc_description':
        'Whether to show interval tabs for switching between different time frames'
        , 'doc_type': 'Boolean', 'doc_default': True}, 'displayMode': {
        'doc_description':
        'The display mode of the widget (e.g., "regular", "compact")',
        'doc_type': 'String', 'doc_default': 'regular'}, 'locale': {
        'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'width': {'doc_description':
        'Width of the widget', 'doc_type': 'String', 'doc_default': '100%'},
        'height': {'doc_description': 'Height of the widget', 'doc_type':
        'String', 'doc_default': '100%'}}


def sparta_99e39c7898() ->dict:
    """
    Stock Heatmap
    """
    return {'symbol': {'doc_description':
        'The symbol of the financial instrument to display (e.g., NASDAQ:AAPL)'
        , 'doc_type': 'String', 'doc_default': 'NASDAQ:AAPL'}, 'width': {
        'doc_description': 'Width of the widget', 'doc_type': 'String',
        'doc_default': '100%'}, 'height': {'doc_description':
        'Height of the widget', 'doc_type': 'String', 'doc_default': '100%'
        }, 'isTransparent': {'doc_description':
        'Whether the widget background is transparent', 'doc_type':
        'Boolean', 'doc_default': False}, 'colorTheme': {'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}}


def sparta_d77fcd7d2c() ->dict:
    """
    Stock Heatmap
    """
    return {'feedMode': {'doc_description':
        'The mode for the data feed, determining which symbols are included (e.g., "all_symbols", "single_symbol")'
        , 'doc_type': 'String', 'doc_default': 'all_symbols'}, 'width': {
        'doc_description': 'Width of the widget', 'doc_type': 'String',
        'doc_default': '100%'}, 'height': {'doc_description':
        'Height of the widget', 'doc_type': 'String', 'doc_default': '100%'
        }, 'displayMode': {'doc_description':
        'The display mode of the widget (e.g., "regular", "compact")',
        'doc_type': 'String', 'doc_default': 'regular'}, 'isTransparent': {
        'doc_description': 'Whether the widget background is transparent',
        'doc_type': 'Boolean', 'doc_default': False}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}}


def sparta_9b3bcd4873() ->dict:
    """
    Stock Heatmap
    """
    return {'symbol': {'doc_description':
        'The symbol of the financial instrument to display (e.g., NASDAQ:AAPL)'
        , 'doc_type': 'String', 'doc_default': 'NASDAQ:AAPL'}, 'dateRange':
        {'doc_description':
        'The date range for the data displayed in the widget (e.g., "1D", "5D", "1M", "3M", "6M", "12M", "YTD", "ALL")'
        , 'doc_type': 'String', 'doc_default': '12M'}, 'autosize': {
        'doc_description':
        'Automatically size the widget to fit its container', 'doc_type':
        'Boolean', 'doc_default': True}, 'width': {'doc_description':
        'Width of the widget', 'doc_type': 'String', 'doc_default': '100%'},
        'height': {'doc_description': 'Height of the widget', 'doc_type':
        'String', 'doc_default': '100%'}, 'isTransparent': {
        'doc_description': 'Whether the widget background is transparent',
        'doc_type': 'Boolean', 'doc_default': False}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}, 'largeChartUrl': {
        'doc_description':
        'URL for displaying a larger version of the chart', 'doc_type':
        'String', 'doc_default': ''}}


def sparta_2f347beff0() ->dict:
    """
    Stock Heatmap
    """
    return {'symbol': {'doc_description':
        'The symbol of the financial instrument to display (e.g., NASDAQ:AAPL)'
        , 'doc_type': 'String', 'doc_default': 'NASDAQ:AAPL'}, 'width': {
        'doc_description': 'Width of the widget', 'doc_type': 'String',
        'doc_default': '100%'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'isTransparent': {
        'doc_description': 'Whether the widget background is transparent',
        'doc_type': 'Boolean', 'doc_default': False}}


def sparta_33d29d8f3e() ->dict:
    """
    Stock Heatmap
    """
    return {'symbol': {'doc_description':
        'The symbol of the financial instrument to display (e.g., NASDAQ:AAPL)'
        , 'doc_type': 'String', 'doc_default': 'NASDAQ:AAPL'}, 'width': {
        'doc_description': 'Width of the widget', 'doc_type': 'String',
        'doc_default': '100%'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'isTransparent': {
        'doc_description': 'Whether the widget background is transparent',
        'doc_type': 'Boolean', 'doc_default': False}}


def sparta_395796e8db() ->dict:
    """
    Stock Heatmap
    """
    return {'symbol': {'doc_description':
        'The symbol of the financial instrument to display (e.g., NASDAQ:AAPL)'
        , 'doc_type': 'String', 'doc_default': 'NASDAQ:AAPL'}, 'width': {
        'doc_description': 'Width of the widget', 'doc_type': 'String',
        'doc_default': '100%'}, 'locale': {'doc_description':
        'The language of the widget interface (e.g., "en" for English, "fr" for French)'
        , 'doc_type': 'String', 'doc_default': 'en'}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'isTransparent': {
        'doc_description': 'Whether the widget background is transparent',
        'doc_type': 'Boolean', 'doc_default': False}}


def sparta_4a73f5ac4d() ->dict:
    """
    Stock Heatmap
    """
    return {'symbols': {'doc_description':
        'List of token to include in the widget', 'doc_type': 'list',
        'doc_default':
        """
[
    {
        "proName": "FOREXCOM:SPXUSD",
        "title": "S&P 500"
    },
    {
        "proName": "FOREXCOM:NSXUSD",
        "title": "US 100"
    },
    {
        "proName": "FX_IDC:EURUSD",
        "title": "EUR to USD"
    },
    {
        "proName": "BITSTAMP:BTCUSD",
        "title": "Bitcoin"
    },
    {
        "proName": "BITSTAMP:ETHUSD",
        "title": "Ethereum"
    }
],
"""
        }, 'isTransparent': {'doc_description':
        'Whether the widget background is transparent', 'doc_type':
        'Boolean', 'doc_default': False}, 'showSymbolLogo': {
        'doc_description': 'Display symbol logo', 'doc_type': 'Boolean',
        'doc_default': True}, 'displayMode': {'doc_description':
        'The display mode of the widget (e.g., "regular", "compact", "adaptive")'
        , 'doc_type': 'String', 'doc_default': 'adaptive'}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'locale': {'doc_description':
        'The language of the widget interface', 'doc_type': 'String',
        'doc_default': 'en'}}


def sparta_a97dd5c9c5() ->dict:
    """
    Stock Heatmap
    """
    return {'symbols': {'doc_description':
        'List of ticker to include in the widget', 'doc_type': 'list',
        'doc_default':
        """
[
    {
        "proName": "FOREXCOM:SPXUSD",
        "title": "S&P 500"
    },
    {
        "proName": "FOREXCOM:NSXUSD",
        "title": "US 100"
    },
    {
        "proName": "FX_IDC:EURUSD",
        "title": "EUR to USD"
    },
    {
        "proName": "BITSTAMP:BTCUSD",
        "title": "Bitcoin"
    },
    {
        "proName": "BITSTAMP:ETHUSD",
        "title": "Ethereum"
    }
    ],
"""
        }, 'isTransparent': {'doc_description':
        'Whether the widget background is transparent', 'doc_type':
        'Boolean', 'doc_default': False}, 'showSymbolLogo': {
        'doc_description': 'Display symbol logo', 'doc_type': 'Boolean',
        'doc_default': True}, 'colorTheme': {'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'locale': {'doc_description':
        'The language of the widget interface', 'doc_type': 'String',
        'doc_default': 'en'}}


def sparta_17030b0b8d() ->dict:
    """
    Stock Heatmap
    """
    return {'dataSource': {'doc_description':
        'The data source for the etf region to load, for instance AllUSEtf',
        'doc_type': 'String', 'doc_default': 'AllUSEtf'}, 'grouping': {
        'doc_description': 'Grouping of the data in the widget', 'doc_type':
        'String', 'doc_default': 'asset_class'}, 'blockSize': {
        'doc_description': 'Size of the block for data representation',
        'doc_type': 'String', 'doc_default': 'aum'}, 'blockColor': {
        'doc_description': 'Color of the block for data representation',
        'doc_type': 'String', 'doc_default': 'change'}, 'locale': {
        'doc_description': 'The language of the widget interface',
        'doc_type': 'String', 'doc_default': 'en'}, 'symbolUrl': {
        'doc_description': 'URL for the symbol used in the widget',
        'doc_type': 'String', 'doc_default': ''}, 'colorTheme': {
        'doc_description':
        'The color theme of the widget (e.g., "light", "dark")', 'doc_type':
        'String', 'doc_default': 'light'}, 'hasTopBar': {'doc_description':
        'Whether the widget has a top bar', 'doc_type': 'Boolean',
        'doc_default': False}, 'isDataSetEnabled': {'doc_description':
        'Enable or disable the data set', 'doc_type': 'Boolean',
        'doc_default': False}, 'isZoomEnabled': {'doc_description':
        'Enable or disable zoom functionality', 'doc_type': 'Boolean',
        'doc_default': True}, 'hasSymbolTooltip': {'doc_description':
        'Display tooltips for symbols', 'doc_type': 'Boolean',
        'doc_default': True}, 'width': {'doc_description':
        'Width of the widget', 'doc_type': 'String', 'doc_default': '100%'},
        'height': {'doc_description': 'Height of the widget', 'doc_type':
        'String', 'doc_default': '100%'}}

#END OF QUBE
