# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, TypedDict  # Added List

import pandas as pd

try:
    from langchain.schema import HumanMessage, SystemMessage
    from langgraph.graph import END, StateGraph
except:
    pass

from tqdm.auto import tqdm

# --- State Definition ---
from ibm_watsonx_gov.metrics.llm_validation.evaluation_criteria import (
    EvaluationCriteria, get_default_evaluation_criteria)


class State(TypedDict):
    model_input: str
    model_output: str
    evaluation_text: str
    evaluation_score: int | None  # Allow None for score
    evaluation_summary: str
    llm: Any
    evaluation_criteria: EvaluationCriteria


# --- Prompt Templates ---
full_response_template = """You are an impartial judge evaluating the quality of an AI model's response. You will receive:

Input: The text the model was asked to process or respond to.
Output: The model's response text.
Your task is to score the model's response on a scale of 1 to 10, considering the following criteria.
You may also consider other relevant factors that contribute to the overall quality of the response.

Evaluation Criteria:
{evaluation_criteria}

Provide a score from 1 to 10 and explain your reasoning clearly and concisely. End the response with 'Final Score: <score>' (e.g., 'Final Score: 7').

Input: '{model_input}'
Output: '{model_output}'
"""

summarization_template = """
You are given an evaluation text produced by a judge model. Summarize the text in a few sentences.
Focus on the core reasoning for the score and the final score itself.
Remove redundancies and make it concise while keeping the essential information.
Disregard the score given by the model and focus on the textual feedback. 

Evaluation Text to Summarize:
{evaluation_text}
"""


# --- Helper Functions ---
def extract_score(evaluation_response: str) -> int | None:
    """Extracts the final score from the evaluation response."""
    match = re.search(r"Final Score: (\d+)",
                      evaluation_response, re.IGNORECASE)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    else:
        # Fallback: look for numbers 1-10 near the end
        potential_scores = re.findall(r'\b([1-9]|10)\b', evaluation_response)
        if potential_scores:
            try:
                return int(potential_scores[-1])  # Take the last one found
            except ValueError:
                return None
    return None


def generate_llm_response(llm: Any, system_prompt: str, human_prompt: str) -> str:
    """Generates a response from the LLM given prompts."""
    try:
        # Ensure prompts are strings
        messages = [
            SystemMessage(content=str(system_prompt)),
            HumanMessage(content=str(human_prompt))
        ]
        results = llm.invoke(messages)
        return results.content
    except Exception as e:
        return f"LLM Error: {e}"


# --- Node Functions ---
def evaluate_response_node(state: State) -> Dict[str, Any]:
    """Evaluates the model's response using the full_response_template."""
    evaluation_criteria_str = state.get(
        "evaluation_criteria", get_default_evaluation_criteria()).to_str()

    formatted_prompt = full_response_template.format(
        model_input=state['model_input'],
        model_output=state['model_output'],
        evaluation_criteria=evaluation_criteria_str
    )
    system_prompt = "You are an impartial judge evaluating an AI model's response."
    evaluation_text = generate_llm_response(
        state["llm"], system_prompt, formatted_prompt)
    score = extract_score(evaluation_text)
    return {"evaluation_text": evaluation_text, "evaluation_score": score}


def summarize_evaluation_node(state: State) -> Dict[str, str]:
    """Summarizes the generated evaluation text."""
    if not state.get("evaluation_text") or "LLM Error" in state["evaluation_text"]:
        return {"evaluation_summary": "Evaluation text missing or contains error."}

    # Use the summarization template as the system prompt directly
    system_prompt = summarization_template.format(
        evaluation_text=state["evaluation_text"])
    # Simpler human prompt
    human_prompt = "Please provide the summary based on the template instructions."
    summary = generate_llm_response(state["llm"], system_prompt, human_prompt)
    return {"evaluation_summary": summary.strip()}


# --- Graph Definition (Unchanged) ---
def get_evaluation_graph():
    """Builds the simplified evaluation workflow."""
    workflow = StateGraph(State)
    workflow.add_node("evaluate_response", evaluate_response_node)
    workflow.add_node("summarize_evaluation", summarize_evaluation_node)
    workflow.set_entry_point("evaluate_response")
    workflow.add_edge("evaluate_response", "summarize_evaluation")
    workflow.add_edge("summarize_evaluation", END)
    app = workflow.compile()
    return app


def _evaluate_row(row: pd.Series, app: Any, llm: Any, input_col: str, output_col: str,
                  text_col: str, score_col: str, summary_col: str, evaluation_criteria: EvaluationCriteria = None) -> pd.Series:
    """
    Helper function to evaluate a single row using the pre-compiled graph.
    To be used with df.apply().
    """
    model_input = row[input_col]
    model_output = row[output_col]

    initial_state: State = {
        "model_input": str(model_input),
        "model_output": str(model_output),
        "llm": llm,
        "evaluation_text": "",
        "evaluation_score": None,  # Initialize score as None
        "evaluation_summary": "",
        "evaluation_criteria": evaluation_criteria,
    }

    try:
        final_state = app.invoke(initial_state)
        return pd.Series({
            text_col: final_state.get("evaluation_text", "Error: Text not generated"),
            # Default to None
            score_col: final_state.get("evaluation_score", None),
            summary_col: final_state.get(
                "evaluation_summary", "Error: Summary not generated")
        })
    except Exception as e:
        return pd.Series({
            text_col: f"Error during processing: {e}",
            score_col: None,  # Error -> None score
            summary_col: f"Error during processing: {e}"
        })


def generate_issues_and_map_to_records(summaries_list: List[str],
                                       llm: Any) -> Dict[str, List[int]]:

    if len(summaries_list) == 0:
        issues_list = []
    elif len(summaries_list) == 1:
        issues_list = summaries_list
    else:
        issues_list = summarize_evaluation_issues(summaries_list, llm)

    # return error
    if is_issues_list_error(issues_list):
        return {issues_list[0]: []}

    # since the same summaries use for issue generation and mapping, issues must apply to the single record
    if len(summaries_list) == 1:
        return {issue: [0] for issue in issues_list}

    return map_issues_to_records(summaries_list, llm, issues_list)


# --- Function to Summarize Issues Across Evaluations ---
def summarize_evaluation_issues(
        summaries_list: List[str],
        llm: Any,
) -> List[str]:
    """
    Analyzes a column of evaluation summaries to identify and rank recurring issues.

    Args:
        summaries_list: The list of record level summaries
        llm: An initialized LangChain compatible LLM instance.
        summary_col: The name of the column containing the evaluation summaries.

    Returns:
        A tuple consisting of:
        A list of strings, each describing a recurring issue, ordered by
        perceived frequency (most frequent first), based on LLM analysis.
        Returns an empty list if no summaries are found or no issues are identified.
        Returns a list containing an error message if the LLM call fails.

        The original dataframe with added relevant recurrent issues from the summary per row.
    """
    valid_summaries = [str(summary) for summary in summaries_list if summary]
    valid_summaries = [
        s for s in valid_summaries
        if not is_summary_error(s)
    ]

    if not valid_summaries:
        return []

    summaries_text = "\n---\n".join(valid_summaries)

    system_prompt = f"""You are an expert analyst reviewing evaluation summaries for AI model responses.
Your task is to identify the main *recurring reasons* or *common negative themes* mentioned across these summaries that might explain why responses were scored lower or deemed problematic.

Based *only* on the provided list of summaries below, list the distinct issues concisely.
Each issue should be concise and focus on a single topic or aspect.
The issues should be distinct: Avoid overlap between the different issues.
Order the list from the most frequently mentioned or most significant issue to the least.
Focus on the *problems* identified in the evaluations.
If no issue are found across the summaries, output "".

Format your output *only* as a numbered list. Do not include any preamble or explanation before the list.

Example Output Format:
1. Response lacks sufficient detail or completeness.
2. Factual inaccuracies present in the response.
3. Output formatting issues (e.g., incorrect markdown).
4. Tone is inappropriate for the context.

Evaluation Summaries to Analyze:
---
{summaries_text}
---
"""
    human_prompt = "Please provide the numbered list of recurring issues based on the summaries above."

    try:
        analysis_result = generate_llm_response(
            llm, system_prompt, human_prompt)

        if "LLM Error:" in analysis_result:
            return [f"LLM Error during issue summarization: {analysis_result}"]
        if not analysis_result or analysis_result == '':
            return []

        issues = []
        lines = [line.strip()
                 for line in analysis_result.strip().split('\n') if line.strip()]
        for line in lines:
            cleaned_line = re.sub(r"^\s*[\d.\-\*]+\s*", "", line).strip()
            if cleaned_line:
                issues.append(cleaned_line)

        return issues

    except Exception as e:
        return [f"Error during issue summarization: {e}"]


# --- Main Evaluation Function ---
def llm_validation_per_record(
        df: pd.DataFrame,
        llm: Any,
        input_col: str = 'model_input',
        output_col: str = 'model_output',
        text_col: str = 'evaluation_text',
        score_col: str = 'evaluation_score',
        summary_col: str = 'evaluation_summary',
        evaluation_criteria: EvaluationCriteria | None = None
) -> pd.DataFrame:
    """
    Evaluates model responses in a DataFrame using a pre-compiled LangGraph.

    Args:
        df: The Pandas DataFrame to process.
        llm: An initialized LangChain compatible LLM instance.
        input_col: Name of the column containing the model input text.
        output_col: Name of the column containing the model output text.
        text_col: Name for the new column for the full evaluation text.
        score_col: Name for the new column for the extracted evaluation score.
        summary_col: Name for the new column for the evaluation summary.
        evaluation_criteria: Optional[EvaluationCriterion] List of evaluation criterion

    Returns:
        The original DataFrame with the new evaluation columns added.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input 'df' must be a Pandas DataFrame.")
    if not llm:
        raise ValueError("LLM instance must be provided.")
    if input_col not in df.columns:
        raise ValueError(f"Input column '{input_col}' not found in DataFrame.")
    if output_col not in df.columns:
        raise ValueError(
            f"Output column '{output_col}' not found in DataFrame.")

    app = get_evaluation_graph()  # Compile the graph once
    tqdm.pandas(desc="Evaluating Rows")
    inputs = [[r, app, llm, input_col, output_col, text_col, score_col,
               summary_col, evaluation_criteria] for i, r in df.iterrows()]
    results = run_func_in_threads(
        _evaluate_row, inputs, progress_desc="Evaluating single records")
    results = pd.DataFrame(results)

    df[text_col] = results[text_col]
    df[score_col] = results[score_col]
    df[summary_col] = results[summary_col]

    return df

#####


def analyze_shortcomings_llm(eval_text, llm, shortcomings):
    """
    Use LLM to analyze evaluation text for shortcomings.
    Returns a list of binary values (0 or 1) indicating presence of each shortcoming.
    """

    if eval_text.startswith("Evaluation text missing"):
        return []

    # Create numbered list of shortcomings for the prompt
    shortcomings_list = "\n".join(
        [f"{i + 1}. {s}" for i, s in enumerate(shortcomings)])
    num_shortcomings = len(shortcomings)

    system_prompt = f"""You are an expert analyst reviewing evaluation feedback for AI model responses.
Your task is to determine which of the following common shortcomings are mentioned or implied in the evaluation text:
{shortcomings_list}
Analyze the evaluation text and determine which shortcomings are present.
For each shortcoming, respond with a 1 if it is mentioned or implied, or 0 if it is not mentioned.
Your response should be a Python list of {num_shortcomings} binary values (0 or 1).
For example: [1,0,0,1,0,0,0] would mean shortcomings 1 and 4 are present, and the others are not.
Respond ONLY with the list in the format [0,1,0,...] with no additional text.
"""

    human_prompt = f"Evaluation text to analyze:\n{eval_text}\n\nWhich shortcomings (1-{num_shortcomings}) are mentioned or implied in this evaluation? Respond with a Python list of {num_shortcomings} binary values (0 or 1) in the format [0,1,0,...]."

    try:
        response = generate_llm_response(
            llm, system_prompt, human_prompt).strip()

        # Extract the list from the response if needed
        if '[' in response and ']' in response:
            response = response[response.find(
                '['):response.find(']') + 1].strip("[]")

        binary_values = response.split(',')

        if len(binary_values) == num_shortcomings:
            return [int(value.strip()) for value in binary_values]

        return ["Error in issues selection: bad response format"]

    except Exception as e:
        return [f"Error in issues selection: {e}"]


def is_summary_error(summary):
    return not summary or summary.startswith("Evaluation text missing or contains error.") or "LLM Error" in summary


def is_issues_list_error(issues_list):
    if len(issues_list) == 1:
        if "Error during issue summarization" in issues_list[0]:
            return True
    return False


def map_issues_to_records(summaries_list: List[str], llm, issues_list=List[str]) -> Dict[str, List[int]]:
    """
    Map each record the relevant issues from issues_list
    returns a dictionary mapping each reccuring issue to the indices of the matching summaries in summaries_list
    """

    # Use provided shortcomings or default to empty list
    if not issues_list:
        return {}

    # return error
    if is_issues_list_error(issues_list):
        return {issues_list[0]: []}

    # Process each evaluation
    issues_counts = {shotrcoming: 0 for shotrcoming in issues_list}
    recurring_issues_per_record = []

    input_list = [[record_summary, llm, issues_list]
                  for record_summary in summaries_list]
    results = run_func_in_threads(analyze_shortcomings_llm, input_list, error_prefix="Error in issues selection",
                                  progress_desc="Mapping issues to records")

    for i, detected_issues_result in enumerate(results):
        if not detected_issues_result:
            identified_issues = []
        elif len(detected_issues_result) == 1 and isinstance(detected_issues_result[0], str):
            identified_issues = detected_issues_result
        else:
            # Create a list of identified shortcomings for this evaluation
            identified_issues = [issues_list[i] for i in range(
                len(issues_list)) if detected_issues_result[i] == 1]
            for issue in identified_issues:
                issues_counts[issue] += 1

        recurring_issues_per_record.append(identified_issues)

    issues_stats = list(issues_counts.items())
    issues_stats.sort(key=lambda x: x[1], reverse=True)
    sorted_issues = [issue[0] for issue in issues_stats]
    issue_to_matching_record_ids = {s: [] for s in sorted_issues}

    for rec_i, record_issues in enumerate(recurring_issues_per_record):
        for record_issue in record_issues:
            issue_to_matching_record_ids[record_issue].append(rec_i)

    return issue_to_matching_record_ids


def reverse_mapping(mapping):
    """
    Reverses a mapping from keys to index lists .
    Uses the order of keys in the original mapping to produce a reverse mapping:
    index -> list of key indices.

    Args:
        mapping (dict): Mapping from keys to list of indices.

    Returns:
        dict: Mapping from index to list of key positions (ints).
    """
    reversed_map = defaultdict(list)

    for i, key in enumerate(mapping):
        for index in mapping[key]:
            reversed_map[index].append(i)

    return dict(reversed_map)


def run_func_in_threads(func, input_list, max_workers=10, error_prefix="Error: ", progress_desc="Processing tasks"):
    if len(input_list) == 1:
        return [func(*input_list[0])]

    results = [None] * len(input_list)
    with ThreadPoolExecutor(max_workers) as executor:
        future_to_input_idx = {executor.submit(func, *input_list[i]): i
                               for i, _ in enumerate(input_list)}
        for future in tqdm(as_completed(future_to_input_idx), total=len(input_list), desc=progress_desc):
            try:
                result = future.result()
            except Exception as e:
                result = [f"{error_prefix}: {e}"]
            results[future_to_input_idx[future]] = result

        return results
