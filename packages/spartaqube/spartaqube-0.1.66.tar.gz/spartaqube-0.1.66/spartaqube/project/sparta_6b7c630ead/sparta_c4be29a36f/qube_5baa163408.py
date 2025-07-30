import json
import io
import os
import base64
import pandas as pd
import quantstats as qs
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO


def sparta_a211b8ced8(df):
    """
    Convert the datetime index of a DataFrame to timezone-naive.Args:
    df (pd.DataFrame): Input DataFrame with datetime index.Returns:
    pd.DataFrame: DataFrame with timezone-naive datetime index."""
    if pd.api.types.is_datetime64_any_dtype(df.index):
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
    return df


def sparta_ffe541c022(series: pd.Series) ->bool:
    """
    Ensure the provided series is a returns series.If a price series is detected, convert it to returns.Parameters:
    series (pd.Series): The input series, which could be prices or returns.Returns:
    pd.Series: A returns series."""
    if (series >= 0).all():
        if series.max() > 1.0:
            return False
    return True


def sparta_1862a69076(fig):
    """
    
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return image_base64


def sparta_92e58c301f(fig):
    """
    
    """
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    return encoded


import quantstats._plotting.core as qscore
import matplotlib.pyplot as _plt
from matplotlib.ticker import FuncFormatter as _FuncFormatter
import pandas as _pd
import numpy as _np


def sparta_83336f5647(x):
    return (x + 1).cumprod()


class _Stats:
    compsum = staticmethod(_compsum)


try:
    from quantstats import stats as _stats
except ImportError:
    _stats = _Stats()


def sparta_8396550222(grayscale):
    _FLATUI_COLORS = ['#FEDD78', '#348DC1', '#BA516B', '#4FA487', '#9B59B6',
        '#613F66', '#84B082', '#DC136C', '#559CAD', '#4A5899']
    _GRAYSCALE_COLORS = ['#000000', '#222222', '#555555', '#888888',
        '#AAAAAA', '#CCCCCC', '#EEEEEE', '#333333', '#666666', '#999999']
    colors = _FLATUI_COLORS
    ls = '-'
    alpha = 0.8
    if grayscale:
        colors = _GRAYSCALE_COLORS
        ls = '-'
        alpha = 0.5
    return colors, ls, alpha


def sparta_77d8edd80d(x, _):
    return f'{x * 100:.0f}%'


def safe_plot_timeseries(returns, benchmark=None, title='Returns', compound
    =False, cumulative=True, fill=False, returns_label='Strategy', hline=
    None, hlw=None, hlcolor='red', hllabel='', percent=True,
    match_volatility=False, log_scale=False, resample=None, lw=1.5, figsize
    =(10, 6), ylabel='', grayscale=False, fontname='Arial', subtitle=True,
    savefig=None, show=True):
    colors, ls, alpha = sparta_8396550222(grayscale)
    returns = returns.copy().fillna(0)
    if isinstance(benchmark, _pd.Series):
        benchmark = benchmark.copy().fillna(0)
    if match_volatility and benchmark is None:
        raise ValueError('match_volatility requires passing of benchmark.')
    if match_volatility and benchmark is not None:
        bmark_vol = benchmark.std()
        returns = returns / returns.std() * bmark_vol
    if compound:
        if cumulative:
            returns = _stats.compsum(returns)
            if isinstance(benchmark, _pd.Series):
                benchmark = _stats.compsum(benchmark)
        else:
            returns = returns.cumsum()
            if isinstance(benchmark, _pd.Series):
                benchmark = benchmark.cumsum()
    if resample:
        returns = returns.resample(resample)
        returns = returns.last() if compound else returns.sum()
        if isinstance(benchmark, _pd.Series):
            benchmark = benchmark.resample(resample)
            benchmark = benchmark.last() if compound else benchmark.sum()
    fig, ax = _plt.subplots(figsize=figsize)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.suptitle(title, y=0.94, fontweight='bold', fontname=fontname,
        fontsize=14, color='black')
    if subtitle and isinstance(returns.index, _pd.DatetimeIndex) and len(
        returns.index) >= 2:
        ax.set_title('%s - %s\n' % (returns.index[0].strftime("%e %b '%y"),
            returns.index[-1].strftime("%e %b '%y")), fontsize=12, color='gray'
            )
    fig.set_facecolor('white')
    ax.set_facecolor('white')
    if isinstance(benchmark, _pd.Series):
        ax.plot(benchmark, lw=lw, ls=ls, label=benchmark.name or
            'Benchmark', color=colors[0])
    alpha = 0.25 if grayscale else 1
    if isinstance(returns, _pd.Series):
        ax.plot(returns, lw=lw, label=returns.name or returns_label, color=
            colors[1], alpha=alpha)
    elif isinstance(returns, _pd.DataFrame):
        for i, col in enumerate(returns.columns):
            ax.plot(returns[col], lw=lw, label=col, alpha=alpha, color=
                colors[i + 1])
    if fill:
        if isinstance(returns, _pd.Series):
            ax.fill_between(returns.index, 0, returns, color=colors[1],
                alpha=0.25)
        elif isinstance(returns, _pd.DataFrame):
            for i, col in enumerate(returns.columns):
                ax.fill_between(returns[col].index, 0, returns[col], color=
                    colors[i + 1], alpha=0.25)
    fig.autofmt_xdate()
    if hline is not None and not isinstance(hline, _pd.Series):
        if grayscale:
            hlcolor = 'black'
        ax.axhline(hline, ls='--', lw=hlw or 1, color=hlcolor, label=
            hllabel, zorder=2)
    ax.axhline(0, ls='-', lw=1, color='gray', zorder=1)
    ax.axhline(0, ls='--', lw=1, color='white' if grayscale else 'black',
        zorder=2)
    try:
        ax.legend(fontsize=11)
    except Exception:
        pass
    _plt.yscale('symlog' if log_scale else 'linear')
    if percent:
        ax.yaxis.set_major_formatter(_FuncFormatter(format_pct_axis))
    ax.set_xlabel('')
    if ylabel:
        ax.set_ylabel(ylabel, fontname=fontname, fontweight='bold',
            fontsize=12, color='black')
    ax.yaxis.set_label_coords(-0.1, 0.5)
    if benchmark is None and len(_pd.DataFrame(returns).columns) == 1:
        try:
            ax.get_legend().remove()
        except Exception:
            pass
    try:
        _plt.subplots_adjust(hspace=0, bottom=0, top=1)
    except Exception:
        pass
    try:
        fig.tight_layout()
    except Exception:
        pass
    if savefig:
        if isinstance(savefig, dict):
            _plt.savefig(**savefig)
        else:
            _plt.savefig(savefig)
    if show:
        _plt.show(block=False)
    _plt.close()
    if not show:
        return fig
    return None


qscore.plot_timeseries = safe_plot_timeseries


def sparta_a1578b82c2(json_data, user_obj) ->dict:
    """
    Backend for Quantstats
    """
    common_props = json.loads(json_data['opts'])
    report_type = int(common_props['reportType'])
    xAxisDataArr = json.loads(json_data['xAxisDataArr'])[0]
    yAxisDataArr = json.loads(json_data['yAxisDataArr'])
    rf = 0
    if 'riskFreeRate' in common_props:
        rf = float(common_props['riskFreeRate'])
    benchmark_title = 'Benchmark'
    strategy_title = 'Strategy'
    if 'strategyTitle' in common_props:
        strategy_title_tmp = common_props['strategyTitle']
        if strategy_title_tmp is not None:
            if len(strategy_title_tmp) > 0:
                strategy_title = strategy_title_tmp
    if 'benchmark_title' in common_props:
        benchmark_title_tmp = common_props['benchmark_title']
        if benchmark_title_tmp is not None:
            if len(benchmark_title_tmp) > 0:
                benchmark_title = benchmark_title_tmp
    title = 'Strategy Tearsheet'
    if 'title' in common_props:
        title_tmp = common_props['title']
        if len(title_tmp) > 0:
            title = title_tmp
    returns_df = pd.DataFrame(yAxisDataArr[0])
    returns_df['date'] = pd.to_datetime(xAxisDataArr)
    returns_df.set_index('date', inplace=True)
    returns_df.columns = ['Portfolio']
    returns_df = sparta_a211b8ced8(returns_df)
    returns_series = returns_df['Portfolio']
    if not sparta_ffe541c022(returns_series):
        returns_series = returns_series.pct_change().dropna()
    benchmark_series = None
    if len(yAxisDataArr) == 2:
        benchmark_df = pd.DataFrame(yAxisDataArr[1])
        benchmark_df['date'] = pd.to_datetime(xAxisDataArr)
        benchmark_df.set_index('date', inplace=True)
        benchmark_df.columns = ['Benchmark']
        benchmark_df = sparta_a211b8ced8(benchmark_df)
        benchmark_series = benchmark_df['Benchmark']
        if not sparta_ffe541c022(benchmark_series):
            benchmark_series = benchmark_series.pct_change().dropna()
    if 'bHtmlReport' in list(json_data.keys()):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir,
            'quantstats/quantstats-tearsheet.html')
        with open(template_path, mode='a') as f:
            f.close()
        qs.reports.html(returns_series, benchmark=benchmark_series, rf=rf,
            mode='full', match_dates=True, output=template_path, title=
            title, strategy_title=strategy_title, benchmark_title=
            benchmark_title)
        with open(template_path, 'rb') as file:
            file_content = file.read()
        return {'res': 1, 'file_content': file_content.decode('utf-8'),
            'b_downloader': True}
    if report_type == 0:

        def get_quantstats_charts(data, benchmark=None):
            encoded_figs = []
            fig_basic = qs.plots.snapshot(data, show=False, strategy_title=
                strategy_title, benchmark_title=benchmark_title)
            encoded_figs.append(sparta_92e58c301f(fig_basic))
            fig_heatmap = qs.plots.monthly_heatmap(data, show=False, ylabel
                =False, returns_label=strategy_title)
            encoded_figs.append(sparta_92e58c301f(fig_heatmap))
            if benchmark is not None:
                fig_heatmap = qs.plots.monthly_heatmap(benchmark, show=
                    False, ylabel=False, returns_label=benchmark_title)
                encoded_figs.append(sparta_92e58c301f(fig_heatmap))
            return encoded_figs
        if len(yAxisDataArr) == 1:
            encoded_charts = get_quantstats_charts(returns_series)
            output = encoded_charts
        elif len(yAxisDataArr) == 2:
            encoded_charts = get_quantstats_charts(returns_series,
                benchmark_series)
            output = encoded_charts
    elif report_type == 1:
        if len(yAxisDataArr) == 1:
            metrics_basic = qs.reports.metrics(returns_series, rf=rf, mode=
                'basic', display=False, strategy_title=strategy_title,
                benchmark_title=benchmark_title)
        elif len(yAxisDataArr) == 2:
            metrics_basic = qs.reports.metrics(returns_series, benchmark=
                benchmark_series, rf=rf, mode='basic', display=False,
                strategy_title=strategy_title, benchmark_title=benchmark_title)
        output = metrics_basic.to_json(orient='split')
    elif report_type == 2:

        def get_quantstats_charts(data, benchmark=None):
            encoded_figs = []
            if common_props['returns']:
                fig_returns = qs.plots.returns(data, benchmark=benchmark,
                    show=False, ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_returns))
            if common_props['logReturns']:
                fig_log_returns = qs.plots.log_returns(data, benchmark=
                    benchmark, show=False, ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_log_returns))
            if common_props['yearlyReturns']:
                fig_yearly_returns = qs.plots.yearly_returns(data,
                    benchmark=benchmark, show=False, ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_yearly_returns))
            if common_props['dailyReturns']:
                fig_daily_returns = qs.plots.daily_returns(data, benchmark=
                    benchmark, show=False, ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_daily_returns))
            if common_props['histogram']:
                fig_hist = qs.plots.histogram(data, benchmark=benchmark,
                    show=False, ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_hist))
            if common_props['rollingVol']:
                fig_rolling_vol = qs.plots.rolling_volatility(data,
                    benchmark=benchmark, show=False, ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_rolling_vol))
            if common_props['rollingSharpe']:
                fig_rolling_sharpe = qs.plots.rolling_sharpe(data,
                    benchmark=benchmark, show=False, ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_rolling_sharpe))
            if common_props['rollingSortino']:
                fig_rolling_sortino = qs.plots.rolling_sortino(data,
                    benchmark=benchmark, show=False, ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_rolling_sortino))
            if common_props['rollingBeta']:
                if benchmark is not None:
                    fig_rolling_beta = qs.plots.rolling_beta(data,
                        benchmark=benchmark, show=False, ylabel=False)
                    encoded_figs.append(sparta_92e58c301f(fig_rolling_beta)
                        )
            if common_props['distribution']:
                fig_distribution = qs.plots.distribution(data, show=False,
                    ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_distribution))
            if common_props['heatmap']:
                fig_heatmap = qs.plots.monthly_heatmap(data, benchmark=
                    benchmark, show=False, ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_heatmap))
            if common_props['drawdowns']:
                fig_drawdowns = qs.plots.drawdown(data, show=False, ylabel=
                    False)
                encoded_figs.append(sparta_92e58c301f(fig_drawdowns))
            if common_props['drawdownsPeriod']:
                fig_drawdowns_periods = qs.plots.drawdowns_periods(data,
                    show=False, ylabel=False, title=strategy_title)
                encoded_figs.append(sparta_92e58c301f(
                    fig_drawdowns_periods))
            if common_props['returnQuantiles']:
                fig_quantiles = qs.plots.distribution(data, show=False,
                    ylabel=False)
                encoded_figs.append(sparta_92e58c301f(fig_quantiles))
            return encoded_figs
        if len(yAxisDataArr) == 1:
            encoded_charts = get_quantstats_charts(returns_series)
            output = encoded_charts
        elif len(yAxisDataArr) == 2:
            encoded_charts = get_quantstats_charts(returns_series,
                benchmark_series)
            output = encoded_charts
    elif report_type == 3:
        data_cols = [strategy_title]
        data_df_all = returns_series
        data_df_all.columns = data_cols
        dd_df = qs.reports._calc_dd(data_df_all)
        dd_info = qs.stats.drawdown_details(data_df_all).sort_values(by=
            'max drawdown', ascending=True)[:10]
        encoded_figs = []
        fig_drawdowns = qs.plots.drawdown(data_df_all, show=False, ylabel=False
            )
        encoded_figs.append(sparta_92e58c301f(fig_drawdowns))
        fig_drawdowns_periods = qs.plots.drawdowns_periods(data_df_all,
            show=False, ylabel=False, title=strategy_title)
        encoded_figs.append(sparta_92e58c301f(fig_drawdowns_periods))
        output = [dd_df.to_json(orient='split'), dd_info.to_json(orient=
            'split'), encoded_figs]
    return {'res': 1, 'reportType': report_type, 'output': output}


def sparta_79270e3648():
    """
    
    """
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch
    from matplotlib.patches import Patch
    import matplotlib.patches as patches


def sparta_2a4f3d80a5(json_data, user_obj) ->dict:
    """
    Backend for Matplotlib
    """
    sparta_79270e3648()
    common_props = json.loads(json_data['opts'])
    x_data_arr = json.loads(json_data['xAxisDataArr'])[0]
    y_data_arr = json.loads(json_data['yAxisDataArr'])
    chart_params_editor_dict = json.loads(json_data['chartParamsEditorDict'])
    print('MATPLOTIB DEBUGGER BACKJEND SERIVCE')
    print('x_data_arr')
    print(x_data_arr)
    print(type(x_data_arr))
    print('y_data_arr')
    print(y_data_arr)
    print(type(y_data_arr))
    print('common_props')
    print(common_props)
    print('chart_params_editor_dict')
    print(chart_params_editor_dict)
    data_df = pd.DataFrame(y_data_arr).T
    data_df.index = x_data_arr
    user_input_y_columns = []
    try:
        user_input_y_columns = [elem['column_renamed'] for elem in
            chart_params_editor_dict['yAxisArr']]
        data_df.columns = user_input_y_columns
    except:
        pass
    user_input_x_columns = []
    try:
        user_input_x_columns = [elem['column_renamed'] for elem in
            chart_params_editor_dict['xAxisArr']]
    except:
        pass
    print('data_df')
    print(data_df)
    print('user_input_x_columns')
    print(user_input_x_columns)
    image_base64 = ''
    type_chart = chart_params_editor_dict['typeChart']
    print('LA type_chart >> ' + str(type_chart))
    if type_chart == 101:
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(1, 1, 1)
        for idx, col in enumerate(list(data_df.columns)):
            this_data = y_data_arr[idx]
            ax.scatter(x_data_arr, this_data, label=col)
        ax.spines['top'].set_color('None')
        ax.spines['right'].set_color('None')
        ax.set_xlabel('Area')
        ax.set_ylabel('Population')
        ax.set_xlim(-0.01)
        ax.legend(loc='upper left', fontsize=10)
        plt.grid()
    elif type_chart == 102:
        import seaborn as sns
        fig, ax = plt.subplots(figsize=(10, 6))
        col_to_plot = list(data_df.columns)
        data_df['sq_index'] = data_df.index
        print('data_df')
        print(data_df)
        for column in user_input_y_columns:
            print(column)
            sns.regplot(x='sq_index', y=column, data=data_df, label=column,
                scatter_kws={'alpha': 0.7}, line_kws={'alpha': 0.7})
        plt.xlabel(user_input_x_columns[0])
        plt.ylabel('')
        plt.legend(title='Category')
        plt.grid()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    try:
        plt.close(fig)
    except:
        pass
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return {'res': 1, 'output': image_base64}

#END OF QUBE
