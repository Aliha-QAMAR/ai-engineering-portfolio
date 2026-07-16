import pandas as pd
from retrieve import retrieve
from answer import generate_grounded_answer
EVAL_SET = [
    {"question": "What is the password requirement?", "answerable": True, "expected_source": "policy.md"},
    {"question": "How many days of annual leave do employees get?", "answerable": True, "expected_source": "policy.md"},
    {"question": "What is the requirement for MFA?", "answerable": True, "expected_source": "policy.md"},
    {"question": "How long is the maternity leave fully paid?", "answerable": True, "expected_source": "policy.md"},
    {"question": "When must leave requests be submitted?", "answerable": True, "expected_source": "policy.md"},
    {"question": "What is required for sick leave exceeding three days?", "answerable": True, "expected_source": "policy.md"},
    {"question": "What is prohibited in the server rooms?", "answerable": True, "expected_source": "policy.md"},
    {"question": "What must visitors do inside corporate systems?", "answerable": True, "expected_source": "policy.md"},
    {"question": "What is the kitchen lunch timing?", "answerable": False, "expected_source": None},
    {"question": "How can I apply for a car allowance?", "answerable": False, "expected_source": None},
    {"question": "What is the company office dress code?", "answerable": False, "expected_source": None},
    {"question": "Who is the current CEO of the company?", "answerable": False, "expected_source": None}
]

def run_evaluation():
    print("\nStarting Honest Measurement RAG Evaluation...")
    total_queries = len(EVAL_SET)
    
    retrieval_hits = 0
    correct_answers = 0
    citations_present = 0
    correct_refusals = 0
    total_unanswerable = sum(1 for q in EVAL_SET if not q["answerable"])
    total_answerable = total_queries - total_unanswerable

    results_log = []

    for idx, item in enumerate(EVAL_SET, 1):
        q = item["question"]
        is_answerable = item["answerable"]
        expected_src = item["expected_source"]
        
        # 1. Retrieve (Top-k=2)
        chunks = retrieve(q, k=2, debug=False)
        
        # Check Retrieval Hit-Rate
        retrieved_sources = [c["metadata"].get("source") for c in chunks]
        hit = False
        if is_answerable and expected_src in retrieved_sources:
            hit = True
            retrieval_hits += 1
        answer, citations = generate_grounded_answer(q, chunks)
        refused = "sorry" in answer.lower() or "do not have enough evidence" in answer.lower() or "not found" in answer.lower()
        ans_acc = False
        if is_answerable:
            if not refused and ("mfa" in answer.lower() or "leave" in answer.lower() or "password" in answer.lower() or "security" in answer.lower() or "maternity" in answer.lower()):
                correct_answers += 1
                ans_acc = True
            if citations:
                citations_present += 1
        else:
            if refused:
                correct_refusals += 1
                correct_answers += 1
                ans_acc = True

        results_log.append({
            "Question": q,
            "Answerable": is_answerable,
            "Retrieved Hit": hit if is_answerable else "N/A",
            "Refused Correctly": refused if not is_answerable else "N/A",
            "Citation Given": len(citations) > 0 if is_answerable else "N/A",
            "Success": ans_acc
        })
    retrieval_hit_rate = (retrieval_hits / total_answerable) * 100
    answer_accuracy = (correct_answers / total_queries) * 100
    citation_rate = (citations_present / total_answerable) * 100
    refusal_accuracy = (correct_refusals / total_unanswerable) * 100

    print("\n" + "="*40)
    print("         EVALUATION REPORT CARD         ")
    print("="*40)
    print(f"Retrieval Hit-Rate:     {retrieval_hit_rate:.1f}%  (Target: High)")
    print(f"Overall Answer Accuracy: {answer_accuracy:.1f}%")
    print(f"Citation Presence Rate:  {citation_rate:.1f}%")
    print(f"Refusal Accuracy:        {refusal_accuracy:.1f}%")
    print("="*40)

    df = pd.DataFrame(results_log)
    df.to_csv("evaluation_results.csv", index=False)
    print("Saved complete evaluation logs to 'evaluation_results.csv'!")

if __name__ == "__main__":
    run_evaluation()