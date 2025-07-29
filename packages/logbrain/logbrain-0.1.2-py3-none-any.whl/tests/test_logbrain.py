
from logbrain import logbrain

def test_basic_analysis():
    brain = logbrain.LogBrain("pattern_config.json", "story.txt", is_file=True)
    lines = [
        "ERROR: cron job failed at 02:30",
        "FAIL: could not execute script"
    ]
    brain.analyze_log("log1.txt", lines)
    brain.finalize(use_llm=False)
    summary = brain.summarize()
    assert "log1.txt" in summary["logs"]
    assert summary["logs"]["log1.txt"]["label"] == "CRON"
    print("Test passed.")
