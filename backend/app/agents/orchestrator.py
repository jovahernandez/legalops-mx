"""
Agent Orchestrator – loads YAML definitions, runs workflows through mock LLM,
and enforces policy checks on all outputs.
"""

import os
import yaml
from typing import Any
from pathlib import Path

from app.agents.openai_llm import OpenAIProvider
from app.agents.policy_engine import PolicyEngine

DEFINITIONS_DIR = Path(__file__).parent / "definitions"


class AgentOrchestrator:
    def __init__(self):
        self.llm = OpenAIProvider()
        self.policy = PolicyEngine()
        self._definitions: dict[str, dict] = {}
        self._load_definitions()

    def _load_definitions(self):
        """Load all YAML agent definitions from the definitions directory."""
        if not DEFINITIONS_DIR.exists():
            return
        for yaml_file in DEFINITIONS_DIR.glob("*.yaml"):
            with open(yaml_file, "r", encoding="utf-8") as f:
                defn = yaml.safe_load(f)
                if defn and "name" in defn:
                    self._definitions[defn["name"]] = defn

    def available_agents(self) -> list[str]:
        return list(self._definitions.keys())

    def list_definitions(self) -> list[dict]:
        """Return summary of each agent (for the API)."""
        return [
            {
                "name": d["name"],
                "purpose": d.get("purpose", ""),
                "boundaries": d.get("boundaries", []),
                "workflow_steps": [s.get("name", s.get("step", "")) for s in d.get("workflow_steps", [])],
            }
            for d in self._definitions.values()
        ]

    def get_definition(self, agent_name: str) -> dict | None:
        return self._definitions.get(agent_name)

    def run(self, agent_name: str, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute an agent workflow and return structured output."""
        defn = self._definitions.get(agent_name)
        if not defn:
            return {"error": f"Agent '{agent_name}' not found"}

        # Build prompt from definition templates
        prompt = self._build_prompt(defn, input_data)

        # Run through mock LLM
        raw_output = self.llm.generate(agent_name, prompt, input_data)

        # Structure the output
        output = self._structure_output(agent_name, defn, raw_output, input_data)

        # Policy engine check (UPL guard)
        output = self.policy.check_and_annotate(output)

        # Always flag that human approval is required
        output["requires_approval"] = True
        output["disclaimer"] = defn.get("disclaimer", "This output requires review by a licensed professional.")

        return output

    def _build_prompt(self, defn: dict, input_data: dict) -> str:
        """Combine definition templates with input data into a prompt."""
        parts = [f"Agent: {defn['name']}", f"Purpose: {defn.get('purpose', '')}"]

        boundaries = defn.get("boundaries", [])
        if boundaries:
            parts.append("Boundaries: " + "; ".join(boundaries))

        for step in defn.get("workflow_steps", []):
            template = step.get("prompt_template", "")
            # Simple variable substitution
            for key, value in input_data.items():
                template = template.replace(f"{{{{{key}}}}}", str(value))
            parts.append(f"Step [{step.get('name', '?')}]: {template}")

        return "\n".join(parts)

    def _structure_output(self, agent_name: str, defn: dict, raw: str, input_data: dict) -> dict:
        """Build the structured output expected by consumers."""
        # Extract questions to ask (mock: based on "Missing" in output)
        questions = []
        if "Missing" in raw or "faltante" in raw.lower() or "needs input" in raw.lower():
            for field in defn.get("required_input_fields", []):
                if field not in input_data or not input_data[field]:
                    questions.append(f"Please provide: {field}")

        # Build next actions from workflow steps
        next_actions = []
        for step in defn.get("workflow_steps", []):
            action = step.get("creates_task")
            if action:
                next_actions.append(action)

        return {
            "agent_name": agent_name,
            "case_packet": raw,
            "questions_to_ask": questions,
            "next_actions": next_actions,
            "urgency_flags": self._detect_urgency(input_data),
            "compliance_flags": [],  # Will be populated by policy engine
        }

    def _detect_urgency(self, input_data: dict) -> list[str]:
        """Simple urgency heuristics."""
        flags = []
        text = str(input_data).lower()

        if any(kw in text for kw in ["detained", "detenido", "custody", "jail"]):
            flags.append("DETAINED_PERSON")
        if any(kw in text for kw in ["court date", "hearing", "audiencia"]):
            flags.append("UPCOMING_COURT_DATE")
        if any(kw in text for kw in ["deadline", "vence", "expires"]):
            flags.append("DEADLINE_APPROACHING")
        if any(kw in text for kw in ["deportation", "removal", "deportación"]):
            flags.append("REMOVAL_PROCEEDINGS")

        return flags
