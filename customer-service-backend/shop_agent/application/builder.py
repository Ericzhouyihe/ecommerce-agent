from pathlib import Path

from shop_agent.domain.chitchat.handler import ChitchatHandler
from shop_agent.domain.chitchat.responder import ChitchatResponder
from shop_agent.domain.clarify.responder import ClarifyResponder
from shop_agent.domain.dialogue.engine import DialogueEngine
from shop_agent.domain.knowledge.handler import KnowledgeHandler
from shop_agent.domain.knowledge.intents import KNOWLEDGE_INTENTS
from shop_agent.domain.knowledge.providers import ProductAPIProvider, OrderAPIProvider, FAQProvider, RAGProvider
from shop_agent.domain.knowledge.registry import KnowledgeProviderRegistry
from shop_agent.domain.knowledge.responder import KnowledgeResponder
from shop_agent.domain.plan.turn_planner import TurnPlanner
from shop_agent.domain.plan.validator import TurnPlanValidator
from shop_agent.domain.task.action.builder import build_action_runner
from shop_agent.domain.task.command.processor import CommandProcessor
from shop_agent.domain.task.flow.executor import FlowExecutor
from shop_agent.domain.task.flow.loader import FlowLoader
from shop_agent.domain.task.handler import TaskHandler

_PROJECT_ROOT = Path(__file__).parents[2]
_FLOW_CONFIG_DIR = _PROJECT_ROOT / "flow_config"
_FLOW_CONFIG_FILES = ("user_flows.yml", "system_flows.yml")


def build_dialogue_engine() -> DialogueEngine:
    flow_paths = [_FLOW_CONFIG_DIR / f for f in _FLOW_CONFIG_FILES]
    flows = FlowLoader().load_many(flow_paths)
    return DialogueEngine(
        turn_planner=TurnPlanner(),
        task_handler=TaskHandler(
            flows=flows,
            command_processor=CommandProcessor(),
            flow_executor=FlowExecutor(),
            action_runner=build_action_runner()
        ),
        knowledge_handler=KnowledgeHandler(
            knowledge_intents=KNOWLEDGE_INTENTS,
            knowledge_responder=KnowledgeResponder(),
            provider_registry=KnowledgeProviderRegistry(
                [
                    ProductAPIProvider(),
                    OrderAPIProvider(),
                    FAQProvider(),
                    RAGProvider(),
                ]
            ),
        ),
        chitchat_handler=ChitchatHandler(
            responder=ChitchatResponder()
        ),
        clarify_responder=ClarifyResponder(),
        turn_plan_validator=TurnPlanValidator()
    )
