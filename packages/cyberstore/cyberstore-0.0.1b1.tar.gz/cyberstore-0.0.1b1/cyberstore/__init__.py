# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/27 23:44
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

from .database import (
    NAME,
    DB_PATH,
    get_settings,
    sql,
    put,
    has,
    tb_path,
    read_ck,
    read_mysql,
)

from .expr_db import from_polars

__version__ = "0.0.1b1"


def update():

    """通过配置文件来更新数据，需要遵循统一编写标准，方便后期添加新的数据源"""

    from . import updater
    import ygo
    import ylog

    update_settings = get_settings().get("updates")
    for task, task_conf in update_settings.items():
        ylog.info(f"[{task} config]: {task_conf}")
        mod = ygo.module_from_str(task_conf["mod"])

        for tb_name in mod.CONFIG.keys():
            ygo.delay(updater.submit)(tb_name=tb_name,
                                      fetch_fn=ygo.delay(mod.fetch_fn)(db_conf=task_conf.get("db_conf")),
                                      **task_conf)()
    updater.do(debug_mode=True)


__all__ = [
    "__version__",
    "NAME",
    "DB_PATH",
    "get_settings",
    "sql",
    "put",
    "has",
    "tb_path",
    "read_ck",
    "read_mysql",
    "from_polars",
    "update",
]
