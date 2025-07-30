# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/6 17:15
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 因子数据补齐模块
---------------------------------------------
"""
from collections import defaultdict
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import unquote

import polars as pl
import xcals
import ygo

from ..store import database

if TYPE_CHECKING:
    from .core import Factor


class MissingChecker:
    @staticmethod
    def check_date(fac: 'Factor', beg_date, end_date) -> list[str]:
        """检验数据缺失的日期"""
        dateList = xcals.get_tradingdays(beg_date=beg_date, end_date=end_date)
        if not database.has(fac.tb_name):
            return dateList
        # 查询本地有数据的日期
        fac_path = database.tb_path(fac.tb_name)
        schema = pl.scan_parquet(fac_path).collect_schema()
        columns = schema.names()
        cond = " OR ".join([f"'{col}' IS NOT NULL" for col in columns])
        sql = f"""SELECT date
                    FROM {fac.tb_name}
                WHERE date BETWEEN '{beg_date}' AND '{end_date}'
                    AND ({cond})
                GROUP BY date 
                HAVING count() > 0;"""
        exist_dateList = database.sql(sql, lazy=False)["date"].cast(pl.Utf8).to_list()
        return set(dateList) - set(exist_dateList)

    @staticmethod
    def check_times(fac: 'Factor', date: str, beg_time: str, end_time: str, freq: str) -> set:
        """
        获取指定日期缺失的时间段
        Parameters
        ----------

        Returns
        -------

        """
        tb_name = fac.tb_name
        tb_path = database.tb_path(tb_name) / f"date={date}"
        partition_dirs = glob(str(tb_path / "time=*" / "*.parquet"))
        exists_times = set()
        for p in partition_dirs:
            rel_path = Path(p).relative_to(tb_path)
            parts = dict(part.split("=", 1) for part in rel_path.parts if "=" in part)
            exists_times.add(unquote(parts["time"]))
        need_times = xcals.get_tradingtime(beg_time, end_time, freq)
        return set(need_times) - set(exists_times)

    @staticmethod
    def check_datetimes(fac: 'Factor',
                        beg_date: str,
                        end_date: str,
                        beg_time: str,
                        end_time: str,
                        freq: str) -> defaultdict[set]:
        """
        获取本地已存在的日期时间
        Parameters
        ----------

        Returns
        -------

        """
        missing_datetimes = defaultdict(set)
        for date in xcals.get_tradingdays(beg_date, end_date):
            missing_datetimes[date] = MissingChecker.check_times(fac, date=date, beg_time=beg_time,
                                                                 end_time=end_time, freq=freq)
        return missing_datetimes


class DataCompleter:
    """数据补齐器"""

    @staticmethod
    def complete(missing_config: list[tuple['Factor', dict[str, set]]], n_jobs: int):
        if missing_config:
            with ygo.pool(n_jobs=n_jobs) as go:
                for (fac, missing_datetimes) in missing_config:
                    for date, timeset in missing_datetimes.items():
                        for time_ in timeset:
                            job_name = f"[{fac.name} {date} {time_} completing]"
                            go.submit(fac.get_value, job_name=job_name)(date=date,
                                                                        time=time_,
                                                                        rt=True,
                                                                        avoid_future=True)

                go.do()
