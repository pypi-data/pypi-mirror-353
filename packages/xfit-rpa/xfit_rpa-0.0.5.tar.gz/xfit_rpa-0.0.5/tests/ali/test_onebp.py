import os
import sys
from xfit_rpa.ali.onebp.base import PageContentSummary
from xfit_rpa.core.base import XEngine
from pathlib import Path
from xfit_rpa.ali import OnebpApp, PageContent


def test_onebp_report():
    # 从配置文件创建引擎
    module_file = Path(sys.modules[PageContentSummary.__module__].__file__)
    file_path = module_file.parent / 'onebp.conf.yaml'

    engine = XEngine.from_config(file_path)
    engine.run_all()
