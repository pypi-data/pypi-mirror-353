from .base import XEngine, XExecutor, XAction, ActionType


class PlaywrightExecutor(XExecutor):
    def execute(self, action: XAction):
        locator = self._resolve_locator(action)

        # 自定义逻辑
        if action.action_type == ActionType.CUSTOM:
            await self._execute_custom(action)
        elif action.action_type == ActionType.CLICK:
            await locator.click()
        elif action.action_type == ActionType.INPUT:
            await locator.fill(action.value)
        # ...更多通用操作

    def _resolve_locator(self, action: XAction) -> 'Locator':
        if action.executor_method == "get_by_label":
            return self.page.get_by_label(action.selector)
        elif action.executor_method == "get_by_role":
            return self.page.get_by_role(**action.method_args)
        elif action.executor_method == "locator":
            return self.page.locator(action.selector)
        else:
            raise ValueError(f"未知 executor_method: {action.executor_method}")


class PlaywrightEngine(XEngine):
    executor_class = PlaywrightExecutor
