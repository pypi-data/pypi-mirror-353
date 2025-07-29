from xfit_rpa.core import XEngine, XContext, XApp, XPage, XModule, XAction, ActionType
from xfit_rpa.utils.date_util import DateRangeParser

app_domain = 'https://one.alimama.com'


# 使用示例
class OnebpApp(XApp, register_name="onebp"):
    name = '万相无界'
    pass


class PageContent(XPage, register_name="onebp.content"):
    name = "报表-内容营销"
    _url = 'https://one.alimama.com/index.html#!/report/live_migrate?rptType=live_migrate&bizCode=onebpLive'

    def execute(self, context: XContext):
        exec_context = self._exec_context(context)
        _date_ranges = []
        for val in exec_context.runtime_params.get('_date_ranges', []):
            if isinstance(val, str):
                _date_ranges = _date_ranges + DateRangeParser.parse(val)
            elif isinstance(val, list) and len(val) == 2:
                _date_ranges.append(val)
            else:
                pass
        for date_range in _date_ranges:
            for effectEqual in exec_context.runtime_params.get('_effectEqual', []):
                self.runtime_params['effectEqual'] = effectEqual
                self.runtime_params['startTime'] = date_range[0]
                self.runtime_params['endTime'] = date_range[1]
                super().execute(exec_context)

    def _get_url(self, context: XContext):
        params = self._get_query_params(context)
        context.runtime_params['_req'] = params
        self.url = self._url + "&" + "&".join([f"{k}={v}" for k, v in params.items()])
        return self.url


class PageContentSummary(XModule, register_name="onebp.content.summary"):
    name = "数据汇总"

    def _init_actions(self):
        self.add_action(
            XAction(
                action=ActionType.CONTAINER,
                selector='xpath=//div[contains(@mx-view, "onebp/views/pages/report/sum-card")]',
                children=[
                    XAction(
                        action=ActionType.CONTAINER,
                        selector='xpath=.//span[contains(text(), "显示模式")]/following-sibling::div',
                        children=[
                            XAction(
                                action=ActionType.CLICK,
                                selector='xpath=.//div[contains(text(), "表格")]'
                            )
                        ]
                    ),
                    XAction(
                        action=ActionType.CLICK,
                        selector='xpath=.//button/span[contains(text(), "下载报表")]'
                    )
                ]
            )
        ).add_action(
            XAction(
                action=ActionType.CLICK,
                selector='xpath=.//div[contains(@data-daynamic-view, "onebp/views/pages/report/download-dialog")]'
            )
        )


class PageContentLive(PageContent, register_name="onebp.content-live"):
    name = "报表-内容营销-直播"
    _url = 'https://one.alimama.com/index.html#!/report/live_migrate?rptType=live_migrate&bizCode=onebpLive'


class PageContentShortVideo(PageContent, register_name="onebp.content-shortVideo"):
    name = "报表-内容营销-短视频"
    _url = 'https://one.alimama.com/index.html#!/report/short_video_migrate?rptType=short_video_migrate&bizCode=onebpShortVideo'


class PageContentUnion(PageContent, register_name="onebp.content-union"):
    name = "报表-内容营销-短直联动"
    _url = 'https://one.alimama.com/index.html#!/report/union_migrate?rptType=union_migrate&bizCode=onebpUnion'


class PageDownload(XPage, register_name="onebp.download"):
    name = "报表-下载管理-下载任务管理"
    _url = 'https://one.alimama.com/index.html#!/report/download-list'

    def _do_execute(self, context: XContext):
        # for download_file, upload_file in self.app_context.get_download_files().items():
        #     self._download_file(download_file, upload_file)
        self._download_file('download_file', 'upload_file')

    def _download_file(self, download_file, upload_file):
        pass


def main():
    # 从配置文件创建引擎
    from pathlib import Path
    engine = XEngine.from_config(Path('onebp.conf.yaml').resolve())
    engine.run_all()


if __name__ == "__main__":
    try:
        main()
    finally:
        print("Done")
