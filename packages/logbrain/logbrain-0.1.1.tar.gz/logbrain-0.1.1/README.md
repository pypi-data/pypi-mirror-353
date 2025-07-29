
# 🧠 LogBrain

**LogBrain** is a smart Python log analysis toolkit that merges lightweight machine learning, symbolic reasoning, and story-driven flow graphs. It analyzes logs (text or screenshots), understands their structure, and generates meaningful summaries or problem statements using rule-based or mini-LLM methods.

---

## 🧩 Key Components

### 1. ConfigurablePatternType
- Parses log content using fuzzy logic or ML.
- Can match entries to pre-defined labels like `CRON`, `APP`, etc.
- Fully configurable via `pattern_config.json`.

### 2. CognitiveGraph
- Accepts a story (e.g. application flow) as a `.txt` file or LLM-generated text.
- Builds a flow map and uses it to detect the stage where errors occur.

---

## 📥 Sample Input: Logs

```
ERROR: cron job failed at 02:30
FAIL: could not execute script
```

## 🧠 Sample Summary (Generated via Tiny LLM)
```
The cron job could not execute the script at 02:30.
This failure likely caused the application timeout due to unmet preconditions.
```

---

## 💻 Usage Example

```python
from logbrain.logbrain import LogBrain

logbrain = LogBrain("pattern_config.json", "story.txt", is_file=True)
lines = ["ERROR: cron job failed at 02:30", "FAIL: could not execute script"]
logbrain.analyze_log("log.txt", lines)
logbrain.finalize(use_llm=True)  # Uses mini LLM to build better summary
print(logbrain.summarize())
```

---

## 📁 Files

- `logbrain.py`: Core logic
- `pattern_config.json`: Configurable pattern matching
- `story.txt`: Sample flow for CognitiveGraph
- `test_logbrain.py`: Test case
- `setup.py`, `requirements.txt`: Packaging

---

## 📦 Install & Run

```bash
pip install -r requirements.txt
python test_logbrain.py
```

---

Ready to log with brains! 🧠
