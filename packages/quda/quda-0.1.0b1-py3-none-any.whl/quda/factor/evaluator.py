# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/6 16:01
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 因子调用执行器
---------------------------------------------
"""

import polars as pl
import ygo
import pandas as pd
import ylog

from .consts import (
    FIELD_ASSET,
    FIELD_DATE,
    FIELD_TIME,
    FIELD_VERSION,
    TYPE_FIXEDTIME,
    TYPE_REALTIME,
    INDEX,
    DATE_FORMAT,
)
from ..store import database
from .resolver import TimeResolver
import xcals
import datetime
from pathlib import Path
from .completer import MissingChecker, DataCompleter
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core import Factor, FactorContext

def _get_value_firsttime(fac: 'Factor', date: str) -> pl.DataFrame:
    """
    第一次落数据: 当本地没有数据或者数据都为空


    Parameters
    ----------
    fac : Factor
        因子对象，包含因子计算函数和其他相关信息。
    date : str
        日期，用于指定因子计算的日期，格式为 yyyy-mm-dd

    Returns
    -------
    data : pl.DataFrame | None
        处理后的因子计算结果数据

    Raises
    ------
    Exception
        如果因子计算函数返回的数据为空或数据类型不符合要求，则抛出异常。
    Exception
        如果因子计算结果中缺少必要的 `asset` 列，则抛出异常。
    """
    data = ygo.delay(fac.fn)(this=fac, date=date)()
    if data is None:
        return data
    if not (isinstance(data, (pl.DataFrame, pd.Series, pd.DataFrame))):
        raise Exception("因子计算函数需要返回 polars.DataFrame | pandas.Series | pandas.DataFrame")
    if isinstance(data, (pd.DataFrame, pd.Series)):
        index_levs = data.index.nlevels
        if index_levs == 1:
            assert FIELD_ASSET == data.index.name, f"因子计算结果index中必须包含`{FIELD_ASSET}`"
        else:
            assert FIELD_ASSET in data.index.names, f"因子计算结果index中必须包含`{FIELD_ASSET}`"
        data = pl.from_pandas(data.reset_index())
    if FIELD_ASSET not in data.columns:
        if data.is_empty():
            raise Exception("Empty Value!")
        raise Exception(f"因子计算函数返回值中必须包含`{FIELD_ASSET}`列")
    index = [FIELD_DATE, FIELD_TIME, FIELD_ASSET]
    val_fields = data.drop(index, strict=False).columns

    data = data.unique().fill_nan(None)
    if data.drop_nulls().is_empty():
        raise Exception("Empty Value!")
    if FIELD_DATE not in data.columns:
        data = data.with_columns(pl.lit(date).alias(FIELD_DATE))
    data = data.with_columns(pl.lit(fac.end_time).alias(FIELD_TIME))
    data = data.select(*index, *val_fields, )

    database.put(data, tb_name=fac.tb_name, partitions=[FIELD_DATE, FIELD_TIME])

    return data.sort(index)


class Evaluator:

    @staticmethod
    def get_value(fac: 'Factor', ctx: 'FactorContext') -> pl.DataFrame | None:
        """
        获取指定日期和时间的最新数据。

        Parameters
        ----------
        fac : Factor
            因子对象，包含因子的相关信息。
        ctx: FactorContext
            参数定制
        Returns
        -------
        polars.DataFrame
        """
        date = ctx.date
        if isinstance(date, (datetime.date, datetime.datetime)):
            date = date.strftime(DATE_FORMAT)
        if ctx.rt:
            fac = fac(end_time=ctx.time)
        # 如果avoid_future 为 True, 且查询时间早于因子的结束时间，使用上一个交易日的数据
        val_date = TimeResolver.resolve_date(date=date,
                                             time=ctx.time,
                                             insert_time=fac.insert_time,
                                             avoid_future=ctx.avoid_future)
        if not database.has(Path(fac.tb_name) / f"date={val_date}" / f"time={fac.end_time}"):
            data = _get_value_firsttime(fac=fac, date=val_date)
        else:
            data = database.sql(f"select * from {fac.tb_name} where date='{val_date}' and time='{fac.end_time}';", lazy=True).drop(
                FIELD_VERSION).collect()
        if ctx.codes is None:
            return data
        cols = data.columns
        codes = pl.DataFrame({FIELD_ASSET: ctx.codes})
        return data.join(codes, on=FIELD_ASSET, how='inner')[cols]

    @staticmethod
    def get_value_depends(depends: list['Factor'] | None, ctx: 'FactorContext') -> pl.DataFrame:
        """
        获取依赖因子的值，并合并成一张宽表。

        Parameters
        ----------
        depends : list[Factor] | None
            可选的因子列表，表示依赖的因子。
        ctx: FactorContext
        Returns
        -------
        polars.DataFrame | None

        Notes
        -----
        - 如果 `depends` 为 None 或空列表，则函数直接返回 None。
        - 函数会为每个因子获取其值，并将这些值合并成一个宽表。
        - 如果某个因子的值为 None，则跳过该因子。
        - 存在多列的因子，列名会被重命名，便于阅读与避免冲突, 命名规则为 {fac.name}.<columns>。
        """
        if not depends:
            return
        depend_vals = list()
        for depend in depends:
            val = Evaluator.get_value(fac=depend, ctx=ctx)
            # 重命名columns
            if val is None:
                continue
            columns = val.columns
            if len(columns) > 4:
                new_columns = [
                    col_name if col_name in INDEX else f'{depend.name}.{col_name}' for
                    col_name in
                    columns]
                val.columns = new_columns
            depend_vals.append(val)
        return pl.concat(depend_vals, how="align")

    @staticmethod
    def get_values(fac: 'Factor', ctx: 'FactorContext') -> pl.DataFrame:
        """取值: 指定日期 beg_time -> end_time 的全部值"""

        def fill_forward(val: pl.DataFrame, beg_time_: str, end_time_: str):
            timeList_ = xcals.get_tradingtime(beg_time_, end_time_, ctx.freq)
            time_df = pl.DataFrame({FIELD_TIME: timeList_})
            full_index = val.select(FIELD_DATE, FIELD_ASSET)
            cols = val.columns[3:]
            full_index = full_index.join(time_df, how="cross")
            over_spec = {"partition_by": [FIELD_DATE, FIELD_ASSET], "order_by": [FIELD_TIME]}
            val = full_index.join(val.drop(FIELD_TIME), on=[FIELD_DATE, FIELD_ASSET], how="left")
            val = val.with_columns(pl.all().exclude(INDEX).forward_fill().over(**over_spec))
            return val.select(*INDEX, *cols).sort(INDEX)

        timeList = xcals.get_tradingtime(ctx.beg_time, ctx.end_time, ctx.freq)
        beg_time, end_time = timeList[0], timeList[-1]
        if fac.type == TYPE_FIXEDTIME:
            if beg_time < fac.insert_time <= end_time:
                # beg_time -> self.insert_time中的需要取上一天的
                prev_need_times = xcals.get_tradingtime(beg_time, fac.insert_time)[:-1]
                ctx.time = beg_time
                prev_val = Evaluator.get_value(fac, ctx)
                prev_val = fill_forward(prev_val, beg_time, prev_need_times[-1])
                ctx.time = fac.insert_time
                cur_val = Evaluator.get_value(fac, ctx)
                cur_val = fill_forward(cur_val, fac.insert_time, end_time)
                return pl.concat([prev_val, cur_val])
            else:
                # 所有值都只能取同一天的
                ctx.time = beg_time
                val = Evaluator.get_value(fac, ctx)
                return fill_forward(val, beg_time, end_time)
        else:
            def complete_and_get(date_, beg_time_, end_time_):
                missing_times = MissingChecker.check_times(fac, date=date_, beg_time=beg_time_, end_time=end_time_, freq=ctx.freq)
                if missing_times:
                    DataCompleter.complete([(fac, {date_: missing_times}), ], n_jobs=ctx.n_jobs)
                # 取值
                return database.sql(
                    f"select * from {fac.tb_name} where date='{date_}' and time between '{beg_time_}' and '{end_time_}';",
                    lazy=True).drop(
                    FIELD_VERSION).collect()

            # if beg_time < fac.insert_time <= end_time:
            #     prev_date = xcals.shift_tradeday(ctx.date, -1)
            #     prev_need_times = xcals.get_tradingtime(beg_time, fac.insert_time)[:-1]
            #     prev_val = complete_and_get(prev_date, beg_time, prev_need_times[-1])
            #     cur_val = complete_and_get(ctx.date, fac.insert_time, end_time)
            #     val = pl.concat([prev_val, cur_val])
            # elif fac.insert_time <= beg_time:
            #     # 已经入库：全部值都取当天的
            #     val = complete_and_get(ctx.date, beg_time, end_time)
            # else:
            #     # insert_time > end_time: 全部值只能取上一天的
            #     prev_date = xcals.shift_tradeday(ctx.date, -1)
            #     val = complete_and_get(prev_date, beg_time, end_time)
            val = complete_and_get(ctx.date, beg_time, end_time)
            if ctx.codes is None:
                return val
            cols = val.columns
            codes = pl.DataFrame({FIELD_ASSET: ctx.codes})
            return val.join(codes, on=FIELD_ASSET, how='inner')[cols]

    @staticmethod
    def get_history(fac: 'Factor', ctx: 'FactorContext') -> pl.DataFrame:

        beg_date = xcals.get_recent_tradeday(ctx.beg_date)
        time_ = ctx.time
        # 数据补完后读取
        fac = fac(end_time=time_) if ctx.rt else fac
        missing_datetimes = MissingChecker.check_datetimes(fac,
                                                           beg_date=xcals.shift_tradeday(ctx.beg_date, -1),
                                                           end_date=ctx.end_date,
                                                           beg_time=time_,
                                                           end_time=time_,
                                                           freq=ctx.freq)
        if missing_datetimes:
            DataCompleter.complete(missing_config=[(fac, missing_datetimes)], n_jobs=ctx.n_jobs)

        query_sql = f"""
            SELECT *
            FROM {fac.tb_name}
            WHERE date BETWEEN '{beg_date}' AND '{ctx.end_date}'
            AND time = '{time_}';
            """
        result = database.sql(query_sql, lazy=False).drop(FIELD_VERSION).with_columns(pl.col(FIELD_DATE).cast(pl.Utf8))
        cols = result.columns
        if ctx.avoid_future and time_ < fac.insert_time:
            dateList = xcals.get_tradingdays(beg_date, ctx.end_date)
            next_dateList = xcals.get_tradingdays(xcals.shift_tradeday(beg_date, 1), xcals.shift_tradeday(ctx.end_date, 1))
            shift_date_map = {old_date: next_dateList[i] for i, old_date in enumerate(dateList)}
            result = result.group_by(FIELD_DATE).map_groups(
                lambda df: df.with_columns(pl.lit(shift_date_map[df[FIELD_DATE][0]]).alias(FIELD_DATE)))
        if result is not None and ctx.codes is not None:
            target_index = pl.DataFrame({FIELD_ASSET: ctx.codes})
            result = target_index.join(result, on=FIELD_ASSET, how="left")
        if ctx.codes is not None:
            result = result.join(pl.DataFrame({FIELD_ASSET: ctx.codes}), on=FIELD_ASSET, how="inner")
        # 调整列的顺序
        result = result.select(cols)
        return result.sort(INDEX)