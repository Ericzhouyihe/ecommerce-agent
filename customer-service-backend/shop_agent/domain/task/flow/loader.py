from pathlib import Path

import yaml

from shop_agent.domain.task.flow.models import Flow, FlowsList, FlowSlot
from shop_agent.domain.task.flow.steps import CollectSlotStep, step_from_json


class FlowLoader:
    """从 YAML 文件加载 Flow 定义，返回 FlowsList。"""

    def load_all(self, *paths: str | Path) -> FlowsList:
        """合并多个 YAML 文件（例如 system_flows + user_flows）"""
        merged = FlowsList()
        for path in paths:
            loaded = self.load(path)
            merged.flows.extend(loaded.flows)
            merged.slots.update(loaded.slots)
        return merged

    def load(self, path: Path) -> FlowsList:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        slots = self._load_slots(data.get("slots", {}))
        flows = self._load_flows(data.get("flows", {}), slots)
        return FlowsList(flows=flows, slots=slots)

    def _load_slots(self, slots_data: dict[str, dict]) -> dict[str, FlowSlot]:
        slots = {}
        for slot_name, slot_data in slots_data.items():
            slots[slot_name] = FlowSlot(**slot_data, name=slot_name)
        return slots

    def _load_flows(self, flows_data: dict[str, dict], slots: dict[str, FlowSlot]) -> list[Flow]:
        flows: list[Flow] = []
        for flow_id, flow_data in flows_data.items():
            steps = [step_from_json(raw_step) for raw_step in flow_data.get("steps", [])]
            flow_slots: list[FlowSlot] = []

            for step in steps:
                if isinstance(step, CollectSlotStep):
                    slot = slots.get(step.slot_name)
                    if slot:
                        flow_slots.append(slot)

            flow = Flow(
                id=str(flow_id),
                name=None if flow_data.get("name") is None else str(flow_data.get("name")),
                description=str(flow_data.get("description", "")),
                steps=steps,
                slots=flow_slots,
            )
            flows.append(flow)
        return flows
