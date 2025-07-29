
import json
import difflib
from typing import List, Dict, Any, Union
from collections import defaultdict
import re
import pytesseract
from PIL import Image
import requests

try:
    from transformers import pipeline
    t5_pipeline = pipeline("text2text-generation", model="t5-small")
except Exception:
    t5_pipeline = None


def build_problem_prompt(kedb_summaries: List[str], use_llm: bool = False) -> str:
    system_intro = "The system involves scheduled background jobs (CRON) and a backend application."
    blocks = {"CRON": [], "APP": [], "OTHER": []}

    for summary in kedb_summaries:
        if ":" in summary:
            label, reason = summary.split(":", 1)
            label = label.strip().upper()
            reason = reason.strip()
        else:
            label, reason = "OTHER", summary

        if label in blocks:
            blocks[label].append(reason)
        else:
            blocks["OTHER"].append(reason)

    parts = [system_intro]
    if blocks["CRON"]:
        parts.append("CRON-related issues:")
        parts.extend([f"- {issue}" for issue in blocks["CRON"]])
    if blocks["APP"]:
        parts.append("Application-related problems:")
        parts.extend([f"- {issue}" for issue in blocks["APP"]])
    if blocks["OTHER"]:
        parts.append("Other system anomalies:")
        parts.extend([f"- {issue}" for issue in blocks["OTHER"]])

    parts.append("Based on these observations, generate a flow or diagnosis.")
    final_prompt = "\n".join(parts)

    if use_llm and t5_pipeline:
        result = t5_pipeline(f"Rephrase the problem: {final_prompt}", max_length=120)[0]['generated_text']
        return result

    return final_prompt


class ConfigurablePatternType:
    def __init__(self, config_path: str, ml_model=None):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.ml_model = ml_model

    def match(self, lines: List[str]) -> str:
        combined = " ".join(lines).lower()
        best_score = 0
        best_label = "unknown"
        for label, examples in self.config.items():
            for example in examples:
                score = difflib.SequenceMatcher(None, combined, example.lower()).ratio()
                if score > best_score:
                    best_score = score
                    best_label = label
        return best_label


class CognitiveGraph:
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)

    def ingest_story(self, story_source: Union[str, Dict[str, Any]], is_file=True, summary=None, use_llm=False):
        if is_file and story_source:
            with open(story_source, 'r') as f:
                narrative = f.read()
        elif isinstance(story_source, dict) and story_source.get("llm_api"):
            response = requests.post(
                story_source["endpoint"],
                json={"prompt": story_source["prompt"]}
            )
            narrative = response.json().get("story", "")
        elif summary:
            narrative = build_problem_prompt(summary, use_llm=use_llm)
        else:
            narrative = ""

        steps = re.split(r'\.\s*', narrative.strip('. '))
        last_node = None
        for step in steps:
            step = step.strip()
            if not step:
                continue
            self.nodes.add(step)
            if last_node:
                self.edges[last_node].append(step)
            last_node = step

    def get_block(self, error_line: str) -> str:
        for node in self.nodes:
            if any(word in error_line.lower() for word in node.lower().split()):
                return node
        return "unknown"

    def get_graph(self):
        return {"nodes": list(self.nodes), "edges": dict(self.edges)}


class LogBrain:
    def __init__(self, pattern_config: str, story_source: Union[str, Dict[str, Any]] = None, is_file=True):
        self.pattern_matcher = ConfigurablePatternType(pattern_config)
        self.cognitive_graph = CognitiveGraph()
        self.log_files = {}
        self.story_source = story_source
        self.is_file = is_file
        self.kedb_summary = []
        self.use_llm_prompt = False

    def parse_log_from_text(self, text: str) -> List[str]:
        return text.splitlines()

    def parse_log_from_file(self, filepath: str) -> List[str]:
        with open(filepath, 'r') as f:
            return f.readlines()

    def parse_log_from_image(self, image_path: str) -> List[str]:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.splitlines()

    def analyze_log(self, filename: str, lines: List[str]):
        label = self.pattern_matcher.match(lines)
        blockwise = []
        for line in lines:
            if "ERROR" in line or "FAIL" in line:
                block = self.cognitive_graph.get_block(line)
                blockwise.append((line, block))
        self.kedb_summary.append(f"{label}: {blockwise[0][0]}" if blockwise else label)
        self.log_files[filename] = {
            "label": label,
            "errors": blockwise
        }

    def summarize(self):
        return {
            "logs": self.log_files,
            "cognitive_flow": self.cognitive_graph.get_graph()
        }

    def finalize(self, use_llm=False):
        self.use_llm_prompt = use_llm
        self.cognitive_graph.ingest_story(
            self.story_source,
            is_file=self.is_file,
            summary=self.kedb_summary,
            use_llm=self.use_llm_prompt
        )

    def regenerate_prompt(self) -> str:
        return build_problem_prompt(self.kedb_summary, use_llm=self.use_llm_prompt)
