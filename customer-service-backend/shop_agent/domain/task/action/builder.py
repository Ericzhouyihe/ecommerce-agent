import importlib
import inspect
import pkgutil

from shop_agent.domain.task.action.base import Action
from shop_agent.domain.task.action.builtin.action_listen import ActionListen
from shop_agent.domain.task.action.builtin.action_response import ActionResponse
from shop_agent.domain.task.action.registry import ActionRegistry
from shop_agent.domain.task.action.runner import ActionRunner


def register_builtin_actions(action_runner: ActionRunner) -> None:
    """注册内置操作"""
    action_runner.registry.register(ActionResponse())
    action_runner.registry.register(ActionListen())


def register_custom_actions(action_runner: ActionRunner) -> None:
    """注册自定义操作"""
    package = importlib.import_module("shop_agent.domain.task.action.custom")

    for _, module_name, is_pkg in pkgutil.iter_modules(
        package.__path__, prefix=f"{package.__name__}."
    ):
        if is_pkg:
            continue

        module = importlib.import_module(module_name)

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if not issubclass(obj, Action) or obj is Action:
                continue
            if obj.__module__ != module.__name__:
                continue

            action_runner.registry.register(obj())


def build_action_runner() -> ActionRunner:
    action_runner = ActionRunner(ActionRegistry())
    register_builtin_actions(action_runner)
    register_custom_actions(action_runner)
    return action_runner


if __name__ == "__main__":
    action_runner = build_action_runner()
    print(action_runner)
