import os
import json
import time
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams


def evaluate_similarity_from_files(
    input_path: str,
    expected_path: str,
    output_path: str,
    model_name: str,
):
    """
    Compares LLM outputs to expected outputs using DeepEval's GEval similarity metric.

    Parameters:
        input_path (str): Path to the input JSON file with fields `id`, `input`, `actual_output`.
        expected_path (str): Path to the JSON file containing expected outputs (dict with keys as `id`).
        output_path (str): Path where the similarity evaluation results will be saved.
        model_name (str): Name of the LLM model to use (e.g., "gpt-4o", "gpt-3.5-turbo").
    """

    # === Get OpenAI API Key ===
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
    os.environ["OPENAI_API_KEY"] = api_key

    # === Load JSON Files ===
    with open(input_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    with open(expected_path, "r", encoding="utf-8") as f:
        expected_outputs = json.load(f)

    # === Set up GEval Similarity Metric ===
    similarity_metric = GEval(
        name="Similarity",
        evaluation_params=[
            LLMTestCaseParams.EXPECTED_OUTPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT
        ],
        criteria="The output should semantically match the expected answer.",
        model=model_name,
        threshold=0.5,
        verbose_mode=True
    )

    # === Run Evaluations ===
    results = []
    for item in input_data:
        qid = item["id"]
        expected_output = expected_outputs.get(qid)
        if not expected_output:
            print(f"Skipping ID '{qid}' - no expected output found.")
            continue

        test_case = LLMTestCase(
            input=item["input"],
            actual_output=item["actual_output"],
            expected_output=expected_output
        )

        start_time = time.time()
        score = similarity_metric.measure(test_case)
        latency = round(time.time() - start_time, 3)

        results.append({
            "id": qid,
            "input": item["input"],
            "similarity_score": score,
            "reason": similarity_metric.reason,
            "latency_seconds": latency
        })

    # === Save Output JSON ===
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n Evaluation complete. Results saved to '{output_path}'.")
