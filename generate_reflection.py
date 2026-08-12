import json
from solution.solution import FailureAnalyzer, EvalResult, QAPair

def run():
    with open("artifacts/benchmark_results.json") as f:
        data = json.load(f)
    
    analyzer = FailureAnalyzer()
    
    # 1. Summary
    evals_data = data["results"]
    metrics = {"context_recall": [], "context_precision": [], "faithfulness": [], "relevance": [], "completeness": [], "overall": []}
    
    good, needs_work, critical = 0, 0, 0
    failures = []
    
    for res in evals_data:
        metrics["context_recall"].append(res["context_recall"])
        metrics["context_precision"].append(res["context_precision"])
        metrics["faithfulness"].append(res["faithfulness"])
        metrics["relevance"].append(res["relevance"])
        metrics["completeness"].append(res["completeness"])
        overall = res["overall"]
        metrics["overall"].append(overall)
        
        if overall >= 0.8:
            good += 1
        elif overall >= 0.6:
            needs_work += 1
        else:
            critical += 1
            
        if not res["passed"]:
            qa = QAPair(question=res["question"], expected_answer="")
            qa.id = res["id"]
            ev_res = EvalResult(
                qa_pair=qa,
                actual_answer=res["actual_answer"],
                faithfulness=res["faithfulness"],
                relevance=res["relevance"],
                completeness=res["completeness"],
                passed=res["passed"],
                failure_type=res["failure_type"],
                context_recall=res["context_recall"],
                context_precision=res["context_precision"]
            )
            failures.append(ev_res)
            
    print("--- Section 1 ---")
    for k, v in metrics.items():
        avg = sum(v)/len(v)
        mi = min(v)
        ma = max(v)
        print(f"{k}: avg={avg:.3f}, min={mi:.3f}, max={ma:.3f}")
        
    print(f"Good: {good}, Needs work: {needs_work}, Critical: {critical}")
    
    print("\n--- Section 2: Root Causes ---")
    failures_sorted = sorted(failures, key=lambda x: x.overall_score())
    for f in failures_sorted[:3]:
        cause = analyzer.find_root_cause(f)
        print(f"ID: {f.qa_pair.id} - Root Cause: {cause}")
        
    print("\n--- Section 4: Improvement Log ---")
    print(analyzer.generate_improvement_log(failures_sorted))
    
    print("\n--- Section 4: Suggestions ---")
    print(analyzer.generate_improvement_suggestions(failures_sorted))

if __name__ == "__main__":
    run()
