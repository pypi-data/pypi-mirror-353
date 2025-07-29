import logging
import time
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import wraps
from typing import Dict, Any, Optional, List, Callable, Type, Union, ClassVar

import yaml

logging.basicConfig(level=logging.INFO)

# 类型定义
HookFunc = Callable[..., None]
ParamDict = Dict[str, Any]

DEFAULT_FLOW_CONFIG = {
    "min_sleep": 1.0,
    "max_sleep": 3.0,
    "fixed_sleep": None,  # None表示使用随机范围
    "max_retries": 3,
    "retry_delay": 2.0
}


def log_execution_time(logger=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            if logger:
                logger.info(f"Execution time for {func.__name__}: {execution_time:.4f} seconds")
            else:
                logging.info(f"Execution time for {func.__name__}: {execution_time:.4f} seconds")
            return result

        return wrapper

    return decorator


def with_retry(context_arg: str = 'context'):
    """重试装饰器工厂"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从参数中获取context
            context = kwargs.get(context_arg) or next((arg for arg in args if isinstance(arg, XContext)), None)

            if not context:
                raise ValueError("Context not found for retry mechanism")

            config = context.get_flow_config()
            last_exception = None

            for attempt in range(1, config["max_retries"] + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        logging.info(f"✅ Retry succeeded on attempt {attempt}")
                    return result
                except Exception as e:
                    last_exception = e
                    if attempt < config["max_retries"]:
                        wait_time = config["retry_delay"] * attempt
                        logging.warning(
                            f"⚠️ Attempt {attempt} failed: {str(e)}. "
                            f"Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
            raise last_exception if last_exception else Exception("Retry failed")

        return wrapper

    return decorator


class _ClassMeta(type):
    """元类实现自动注册"""
    _registry: Dict[str, Union[Type['XPage'], Type['XModule']]] = {}

    def __new__(mcls, name, bases, namespace, register_name: str = None):
        cls = super().__new__(mcls, name, bases, namespace)
        if register_name:
            mcls._registry[register_name] = cls
        return cls

    @classmethod
    def get_instance(cls, register_name: str, **kwargs) -> Union['XPage', 'XModule']:
        """按需创建实例"""
        print(cls._registry.keys())
        if register_name not in cls._registry:
            raise ValueError(f"Class {register_name} not registered")
        return cls._registry[register_name](**kwargs)


@dataclass
class XFlowConfig:
    """全局执行控制配置"""
    min_sleep: float = 1.0  # 默认最小睡眠时间(秒)
    max_sleep: float = 3.0  # 默认最大睡眠时间(秒)
    fixed_sleep: Optional[float] = None  # 固定睡眠时间(优先于随机范围)
    max_retries: int = 3  # 默认最大重试次数
    retry_delay: float = 1.0  # 重试间隔(秒)
    retry_exceptions: tuple = (Exception,)  # 触发重试的异常类型

    def get_sleep_time(self) -> float:
        """获取睡眠时间"""
        if self.fixed_sleep is not None:
            return self.fixed_sleep
        import random
        return random.uniform(self.min_sleep, self.max_sleep)


@dataclass
class XContext:
    """RPA 运行时上下文"""
    page: Optional[Any] = None
    locator: Optional[Any] = None
    # {account: {}, oss_list: []}
    global_params: Dict[str, Any] = field(default_factory=dict)
    default_params: Dict[str, Any] = field(default_factory=dict)
    runtime_params: Dict[str, Any] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)
    current_app: Optional[Type['XApp']] = None
    current_page: Optional[Type['XPage']] = None
    current_module: Optional[Type['XModule']] = None

    def get_effective_params(self) -> Dict[str, Any]:
        """获取最终生效的参数，优先级: runtime_params > default_params > global_params"""
        return {
            **self.global_params,
            **self.default_params,
            **self.runtime_params
        }

    def get_flow_config(self) -> Dict[str, Any]:
        """从runtime_params中提取控制配置，合并默认值"""
        runtime_params = self.get_effective_params()
        return {
            **DEFAULT_FLOW_CONFIG,
            **runtime_params.get("flow_config", {})
        }

    def smart_sleep(self):
        """智能睡眠方法"""
        import random
        config = self.get_flow_config()
        sleep_time = config["fixed_sleep"] or random.uniform(config["min_sleep"], config["max_sleep"])
        if sleep_time > 0:
            logging.debug(f"🕒 Sleeping for {sleep_time:.2f}s...")
            time.sleep(sleep_time)
            # await asyncio.sleep(sleep_time)


@dataclass
class XOSS:
    """OSS存储配置"""
    name: str
    params: Dict[str, Any] = field(default_factory=dict)


class LocatorType(Enum):
    """所有支持的元素类型枚举"""
    ID = auto()
    CLASS = auto()
    TAG = auto()
    XPATH = auto()
    LABEL = auto()


class ActionType(Enum):
    """所有支持的动作类型枚举"""
    CLICK = auto()  # 点击元素
    HOVER = auto()  # 悬停元素
    FILL = auto()  # 填写输入框
    SCROLL = auto()  # 滚动到元素
    WAIT = auto()  # 等待元素
    CONTAINER = auto()  # 容器类型（仅用于分组）
    DOUBLE_CLICK = auto()  # 双击
    RIGHT_CLICK = auto()  # 右键点击
    DRAG = auto()  # 拖拽操作
    KEY_PRESS = auto()  # 键盘按键

    @classmethod
    def from_str(cls, value: str) -> 'ActionType':
        """从字符串转换为枚举值（不区分大小写）"""
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Invalid action type: {value}. Valid types are: {[e.name for e in cls]}")


@dataclass
class XAction(metaclass=_ClassMeta):
    # action_type: Union[ActionType, str]  # 支持直接传枚举或字符串
    action: Union[str, dict, Callable]
    name: str = ''
    description: Optional[str] = ''
    selector: str = ""
    default_params: Dict[str, Any] = field(default_factory=dict)
    runtime_params: Dict[str, Any] = field(default_factory=dict)
    children: List['XAction'] = field(default_factory=list)  # 子动作

    def __post_init__(self):
        # 钩子函数默认为空列表
        # logging.info(f'=====xxx======={inspect.currentframe().f_code.co_name} {self.name}')
        logging.info(f'============action.__init__ {self.name}')
        # 统一转换action_type为枚举
        # if isinstance(self.action_type, str):
        #     self.action_type = ActionType.from_str(self.action_type)
        if isinstance(self.action, str):
            self.action = {type: ActionType.from_str(self.action)}
        pass

    def add_child(self, action: 'XAction') -> 'XAction':
        """添加子动作并自动设置父选择器"""
        self.children.append(action)
        return self

    @with_retry()
    @log_execution_time()
    def execute(self, context: XContext):
        # 创建当前action的执行上下文
        exec_context = self._exec_context(context)

        self._before_execute(exec_context)

        # 执行前睡眠
        exec_context.smart_sleep()

        # 执行当前动作
        self._do_execute(exec_context)

        # 执行子动作
        for child in self.children:
            child.execute(exec_context)

        self._after_execute(exec_context)

    def _exec_context(self, context):
        return XContext(
            page=context.page,
            locator=context.locator,
            global_params=context.global_params,
            default_params={**context.default_params, **self.default_params},
            runtime_params={**context.runtime_params, **self.runtime_params},
            state=deepcopy(context.state),
            current_app=context.current_app,
            current_page=context.current_page,
            current_module=context.current_module
        )

    def _do_execute(self, context):
        logging.info(f'============action._do_execute {self.name}')
        if context.page is None:
            # raise ValueError("Page not found. Please set page before execute action.")
            return

        params = context.get_effective_params()
        element = self._get_element(context)
        if len(self.children):
            context.locator = element

        # 执行前睡眠
        # context.smart_sleep()

        # 根据不同类型执行操作
        if callable(self.action):
            self.action()
        elif isinstance(self.action, dict):
            if self.action.type == ActionType.CLICK:
                element.click()
            elif self.action.type == ActionType.HOVER:
                element.hover()
            elif self.action.type == ActionType.FILL:
                element.fill(params.get("value", ""))
            elif self.action.type == ActionType.SCROLL:
                element.scroll_into_view_if_needed()
            elif self.action.type == ActionType.WAIT:
                element.wait_for(timeout=params.get("timeout", 5000))
            # ...其他类型处理...
            elif self.action.type != ActionType.CONTAINER:
                raise NotImplementedError(f"Action type {self.action.type} not implemented")

    def _before_execute(self, context):
        logging.info(f'============action.before_execute {self.name}, {context.runtime_params}')
        pass

    def _after_execute(self, context):
        logging.info(f'============action.after_execute {self.name}')
        pass

    def _get_element(self, context: XContext):
        """获取当前元素"""
        if context.locator is not None:
            locator = context.locator.locator(self.selector)
        else:
            locator = context.page.locator(self.selector)
        # if self.action_type in (ActionType.DRAG, ActionType.SCROLL):
        #     return locator.first  # 某些操作需要具体元素
        return locator

    def __repr__(self):
        return f"XAction({self.action}, {self.selector}, {self.name}, {len(self.children)} children)"


@dataclass
class XModule(metaclass=_ClassMeta):
    name: ClassVar[str]
    description: ClassVar[Optional[str]] = None
    flow_yaml: ClassVar[Optional[str]] = None
    default_params: Dict[str, Any] = field(default_factory=dict)
    runtime_params: Dict[str, Any] = field(default_factory=dict)

    actions: List[XAction] = field(default_factory=list)

    def __post_init__(self):
        # 钩子函数默认为空列表
        logging.info(f'============module.__init__ {self.name}')
        self._init_actions()
        if self.flow_yaml:
            self._load_from_yaml(self.flow_yaml)

    def _init_actions(self):
        # self.add_action(XAction()) \
        #     .add_action(XAction()) \
        #     .add_action(XAction())
        pass

    def _load_from_yaml(self, yaml_path: str):
        from pathlib import Path
        abs_yaml_path = Path(yaml_path).resolve()
        if abs_yaml_path.exists():
            with open(abs_yaml_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
                for action_data in yaml_data['steps']:
                    action = self._parse_action(action_data)
                    self.add_action(action)
        else:
            raise FileNotFoundError(f"YAML file not found: {abs_yaml_path}")
        pass

    def _parse_action(self, action_data: dict) -> XAction:
        """解析动作数据字典"""
        children = action_data.get('children', [])
        action_data.pop('children', None)  # 移除children字段，避免递归解析时重复
        action = XAction(**action_data)
        if len(children):
            for child_data in children:
                child = self._parse_action(child_data)
                action.add_child(child)
        return action

    def add_action(self, action: XAction) -> 'XModule':
        self.actions.append(action)
        return self

    def execute(self, context: XContext):
        exec_context = self._exec_context(context)

        self._before_execute(exec_context)

        # 执行前睡眠
        exec_context.smart_sleep()

        self._do_execute(exec_context)

        self._after_execute(exec_context)

    def _exec_context(self, context: XContext):
        return XContext(
            page=context.page,
            global_params=context.global_params,
            default_params={**context.default_params, **self.default_params},
            runtime_params={**context.runtime_params, **self.runtime_params},
            state=deepcopy(context.state),
            current_app=context.current_app,
            current_page=context.current_page,
            current_module=self
        )

    def _do_execute(self, context: XContext):
        logging.info(f'============module._do_execute {self.name}')
        for action in self.actions:
            action.execute(context)

    def _before_execute(self, context):
        logging.info(f'============module.before_execute {self.name}, {context.runtime_params}')
        pass

    def _after_execute(self, context):
        logging.info(f'============module.after_execute {self.name}')
        pass

    def __repr__(self):
        return f"XModule({self.name}, {self.description})"


@dataclass
class XPage(metaclass=_ClassMeta):
    name: ClassVar[str]
    description: ClassVar[Optional[str]] = None
    url: Optional[str] = None
    default_params: Dict[str, Any] = field(default_factory=dict)
    runtime_params: Dict[str, Any] = field(default_factory=dict)

    task_modules: List[XModule] = field(default_factory=list)

    def __post_init__(self):
        if not self.url and hasattr(self, '_url'):
            self.url = self._url
        # 钩子函数默认为空列表
        logging.info(f'============page.__init__ {self.name}, {self.url}')
        pass

    def add_task_module(self, module: XModule) -> 'XPage':
        self.task_modules.append(module)
        return self

    def execute(self, context: XContext):
        exec_context = self._exec_context(context)

        self._to_url(exec_context)

        self._before_execute(exec_context)

        # 执行前睡眠
        exec_context.smart_sleep()

        self._do_execute(exec_context)

        self._after_execute(exec_context)

    def _exec_context(self, context: XContext):
        return XContext(
            page=context.page,
            global_params=context.global_params,
            default_params={**context.default_params, **self.default_params},
            runtime_params={**context.runtime_params, **self.runtime_params},
            state=deepcopy(context.state),
            current_app=context.current_app,
            current_page=self,
            current_module=None
        )

    def _do_execute(self, context: XContext):
        logging.info(f'============page._do_execute {self.name}')
        for module in self.task_modules:
            module.execute(context)
        pass

    def _before_execute(self, context: XContext):
        logging.info(f'============page.before_execute {self.name}, {self.url}')
        pass

    def _after_execute(self, context: XContext):
        logging.info(f'============page.after_execute {self.name}')
        pass

    def _to_url(self, context: XContext):
        _url = self._get_url(context)
        if _url:
            logging.info(f'============page.to_url {_url}')
            if context.page and hasattr(context.page, 'goto'):
                context.page.goto(_url)
            elif context.page and hasattr(context.page, 'navigate'):
                context.page.navigate(_url)
            else:
                logging.warning(f'============page.to_url {_url} url is empty or goto method not available.')

    def _get_url(self, context: XContext) -> str:
        return self.url

    def _get_query_params(self, context: XContext):
        params = {}
        args = context.get_effective_params()
        for key in args.get('query_params', {}):
            if key in args:
                params[key] = args[key]

        return params

    def __repr__(self):
        return f"XPage({self.name}, {self.description}), {self.url})"


@dataclass
class XApp(metaclass=_ClassMeta):
    name: ClassVar[str]
    description: ClassVar[Optional[str]] = None
    default_params: Dict[str, Any] = field(default_factory=dict)
    runtime_params: Dict[str, Any] = field(default_factory=dict)

    task_pages: List[XPage] = field(default_factory=list)

    def __post_init__(self):
        # 钩子函数默认为空列表
        logging.info(f'============app.__init__ {self.name}')
        pass

    def add_task_page(self, page: XPage) -> 'XApp':
        self.task_pages.append(page)
        return self

    def run(self, page=None, global_params: Dict[str, Any] = None):
        context = XContext(
            page=page,
            global_params=global_params or {},
            default_params=self.default_params,
            runtime_params=self.runtime_params,
            current_app=self
        )

        try:
            self._setup_browser(context)

            self._before_run(context)

            for page in self.task_pages:
                page.execute(context)
            self._after_run(context)

        finally:
            self._cleanup_browser(context)

        return self

    def _setup_browser(self, context: XContext):
        """由子类实现具体的浏览器初始化"""
        # raise NotImplementedError
        pass

    def _cleanup_browser(self, context: XContext):
        """由子类实现具体的资源清理"""
        # raise NotImplementedError
        pass

    def _before_run(self, context: XContext):
        logging.info(f'============app.before_run {self.name}')
        pass

    def _after_run(self, context: XContext):
        logging.info(f'============app.after_run {self.name}')
        pass

    def __repr__(self):
        return f"XApp({self.name}, {self.description}))"


@dataclass
class XEngine:
    """主引擎，支持多个App并行运行"""
    apps: List[XApp] = field(default_factory=list)
    account_list: List[Dict[str, Any]] = field(default_factory=list)
    oss_configs: List[Type['XOSS']] = field(default_factory=list)

    @classmethod
    def from_config(cls, config_path: str) -> 'XEngine':
        return cls.from_config_yaml(config_path)

    @classmethod
    def from_config_yaml(cls, config_path: str) -> 'XEngine':
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return cls.from_config_dict(config)

    @classmethod
    def from_config_dict(cls, config: Dict[str, Any]) -> 'XEngine':
        engine = cls(
            account_list=config.get('account_list', []),
            oss_configs=[XOSS(name=oss['name'], params=oss.get('params', {})) for oss in config.get('oss', [])]
        )

        # 处理多个App配置
        for app_config in config.get('apps', []):
            app = _ClassMeta.get_instance(
                app_config['name'],
                # name=app_config.get('name'),
                default_params=app_config.get('default_params', {}),
                runtime_params=app_config.get('params', {}),
                # oss_configs=deepcopy(engine.oss_configs)
            )

            # 处理页面配置
            for page_config in app_config.get('pages', []):
                page = _ClassMeta.get_instance(
                    page_config['name'] if '.' in page_config[
                        'name'] else f"{app_config['name']}.{page_config['name']}",
                    # name=page_config['name'],
                    url=page_config.get('url', ''),
                    default_params=page_config.get('default_params', {}),
                    runtime_params=page_config.get('params', {})
                )

                # 处理模块配置
                for module_config in page_config.get('modules', []):
                    module = _ClassMeta.get_instance(
                        module_config['name'] if '.' in module_config[
                            'name'] else f"{app_config['name']}.{page_config['name']}.{module_config['name']}",
                        # name=f"{module_config['name']}",
                        default_params=module_config.get('default_params', {}),
                        runtime_params=module_config.get('params', {})
                    )

                    # 处理动作配置
                    for action_config in module_config.get('actions', []):
                        action = XAction(
                            name=action_config.get('name', 'unnamed_action'),
                            action=action_config.get('action', 'click'),
                            selector=action_config.get('selector', ''),
                            default_params=action_config.get('default_params', {}),
                            runtime_params=action_config.get('params', {})
                        )
                        module.actions.append(action)

                    page.add_task_module(module)

                app.add_task_page(page)

            engine.apps.append(app)

        return engine

    def run_all(self, page: [Any, None] = None, global_params: Dict[str, Any] = {}):
        """并行运行所有App"""
        tasks = []
        if len(self.oss_configs) > 0 and len(global_params.get('oss_list', [])) == 0:
            global_params['oss_list'] = self.oss_configs
        if len(self.account_list) > 0:
            for account_info in self.account_list:
                account_params = {**(global_params or {}), 'account': account_info}
                for app in self.apps:
                    tasks.append(app.run(page, account_params))
        else:
            for app in self.apps:
                tasks.append(app.run(page, global_params))

        # await asyncio.gather(*tasks)
