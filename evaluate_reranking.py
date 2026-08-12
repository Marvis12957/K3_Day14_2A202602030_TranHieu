import json
from solution.solution import RAGASEvaluator, QAPair, rerank_by_overlap

def run_evaluation():
    with open("artifacts/actual_answers.json") as f:
        data = json.load(f)["answers"]
    
    with open("golden_dataset.json") as f:
        golden = json.load(f)["qa_pairs"]
        
    golden_dict = {q["id"]: q for q in golden}
    evaluator = RAGASEvaluator()
    
    cases = []
    
    target_ids = ["E04", "M04", "H04", "A01", "A02"]
    
    for item in data:
        q_id = item["id"]
        if q_id not in target_ids:
            continue
            
        golden_q = golden_dict[q_id]
        expected_answer = golden_q["expected_answer"]
        retrieved = item["retrieved_contexts"]
        retrieved_texts = [c["text"] for c in retrieved]
        
        # Before reranking
        recall_before = evaluator.evaluate_context_recall(retrieved_texts, expected_answer)
        precision_before = evaluator.evaluate_context_precision(retrieved_texts, expected_answer)
        
        # After reranking
        reranked = rerank_by_overlap(retrieved_texts, golden_q["question"])
        recall_after = evaluator.evaluate_context_recall(reranked, expected_answer)
        precision_after = evaluator.evaluate_context_precision(reranked, expected_answer)
        
        cases.append({
            "id": q_id,
            "recall_before": recall_before,
            "recall_after": recall_after,
            "precision_before": precision_before,
            "precision_after": precision_after,
            "delta_precision": precision_after - precision_before
        })
        
    print(json.dumps(cases, indent=2))

if __name__ == "__main__":
    run_evaluation()
