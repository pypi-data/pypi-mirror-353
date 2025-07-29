from xfit_rpa.core import XAction, ActionType, XContext


class BaseExecutor:
    def __init__(self, context):
        self.context = context

    async def execute(self, action: XAction):
        raise NotImplementedError


class PlaywrightExecutor(BaseExecutor):
    def __init__(self, page):
        super().__init__(XContext())
        self.page = page

    async def execute(self, action: XAction):
        if action.action_type == ActionType.CLICK:
            locator = self.page.locator('xpath=//button')
            await locator.click()

        elif action.action_type == ActionType.INPUT:
            locator = self.page.locator('xpath=//input')
            await locator.fill(action.value)


class UiBotExecutor(BaseExecutor):
    def __init__(self, uibot):
        super().__init__(XContext())
        self.uibot = uibot

    def execute(self, action: XAction):
        if action.action_type == ActionType.CLICK:
            self.uibot.click(selector=action.selector)
