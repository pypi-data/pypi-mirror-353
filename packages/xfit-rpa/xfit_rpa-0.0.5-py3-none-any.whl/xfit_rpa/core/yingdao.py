from .base import XEngine, XExecutor, XContext, XAction


class YingDaoExecutor(XExecutor):
    def execute(self, action: XAction, context: XContext):
        pass


class YingDaoEngine(XEngine):
    executor_class = YingDaoExecutor
