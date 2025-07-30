# Evaluators

Evaluators are the core components that score model outputs against expected results. They define the criteria by which you measure your model's performance.

## Built-in Evaluators

### exact_match

The `exact_match` evaluator checks for exact string equality between the model output and expected result.

```python
from doteval.evaluators import exact_match

# Simple usage
score = exact_match("42", "42")  # Returns Score(exact_match, True, [accuracy], {...})

# In an evaluation
@foreach("question,answer", dataset)
def eval_math(question, answer, model):
    result = model.generate(question)
    return exact_match(result, answer)
```

## Creating Custom Evaluators

Use the `@evaluator` decorator to create custom scoring functions with associated metrics.

### Basic Custom Evaluator

```python
from doteval.evaluators import evaluator
from doteval.metrics import accuracy

@evaluator(metrics=accuracy())
def contains_keyword(response: str, keyword: str) -> bool:
    """Check if response contains a specific keyword."""
    return keyword.lower() in response.lower()

# Usage
@foreach("prompt,expected_keyword", dataset)
def eval_keyword_presence(prompt, expected_keyword, model):
    response = model.generate(prompt)
    return contains_keyword(response, expected_keyword)
```

### Multi-Metric Evaluator

Attach multiple metrics to a single evaluator:

```python
from doteval.metrics import accuracy, metric

@metric
def precision() -> Metric:
    def calculate(scores: list[bool]) -> float:
        true_positives = sum(scores)
        predicted_positives = len(scores)
        return true_positives / predicted_positives if predicted_positives > 0 else 0.0
    return calculate

@evaluator(metrics=[accuracy(), precision()])
def sentiment_match(predicted: str, expected: str) -> bool:
    """Evaluate sentiment classification accuracy."""
    return predicted.strip().lower() == expected.strip().lower()
```

### Complex Evaluators

For more sophisticated scoring logic:

```python
import re
from typing import Tuple

@evaluator(metrics=accuracy())
def math_reasoning_score(response: str, expected_answer: str) -> bool:
    """
    Evaluate mathematical reasoning by checking:
    1. Final answer correctness
    2. Presence of reasoning steps
    """
    # Extract final answer
    answer_pattern = r"(?:answer|result|solution)(?:\s*[:=]\s*)?(\d+(?:\.\d+)?)"
    match = re.search(answer_pattern, response.lower())

    if not match:
        return False

    predicted_answer = match.group(1)
    return predicted_answer == expected_answer.strip()

# Usage in evaluation
@foreach("problem,solution", math_dataset)
def eval_math_reasoning(problem, solution, model):
    prompt = f"Solve this step by step: {problem}"
    response = model.generate(prompt)
    return math_reasoning_score(response, solution)
```

### Comparative Evaluators

Create evaluators that compare multiple outputs:

```python
@evaluator(metrics=accuracy())
def preference_ranking(response_a: str, response_b: str, human_preference: str) -> bool:
    """Evaluate preference ranking between two responses."""
    # This would typically involve a more sophisticated comparison
    # For demo purposes, we'll use a simple length-based heuristic
    if human_preference == "A":
        return len(response_a) > len(response_b)
    else:
        return len(response_b) > len(response_a)

@foreach("prompt,response_a,response_b,preference", preference_dataset)
def eval_preference(prompt, response_a, response_b, preference, model):
    return preference_ranking(response_a, response_b, preference)
```

## Working with Scores

Evaluators return `Score` objects that contain:

- **name**: The evaluator function name
- **value**: The evaluation result (typically bool, float, or str)
- **metrics**: List of metrics to compute
- **metadata**: Additional context about the evaluation

```python
from doteval.evaluators import exact_match

score = exact_match("hello", "hello")
print(f"Evaluator: {score.name}")         # "exact_match"
print(f"Result: {score.value}")           # True
print(f"Metrics: {score.metrics}")        # [accuracy]
print(f"Metadata: {score.metadata}")      # {"value": "hello", "expected": "hello"}
```

## Multiple Evaluators per Test

Return multiple scores from a single evaluation function:

```python
@foreach("text,expected_sentiment,expected_topic", dataset)
def comprehensive_eval(text, expected_sentiment, expected_topic, model):
    response = model.analyze(text)

    # Multiple evaluation criteria
    sentiment_score = sentiment_match(response.sentiment, expected_sentiment)
    topic_score = exact_match(response.topic, expected_topic)
    length_score = length_check(response.text, min_length=10)

    return sentiment_score, topic_score, length_score
```

## Evaluation Context

Access evaluation metadata within evaluators:

```python
@evaluator(metrics=accuracy())
def context_aware_evaluator(response: str, expected: str, question_type: str) -> bool:
    """Evaluator that adapts behavior based on question type."""
    if question_type == "mathematical":
        # Extract numerical answer for math questions
        return extract_number(response) == extract_number(expected)
    elif question_type == "multiple_choice":
        # Look for letter answers A, B, C, D
        return extract_choice(response) == expected
    else:
        # Default to exact match
        return response.strip() == expected.strip()

def extract_number(text: str) -> str:
    """Extract the first number from text."""
    import re
    match = re.search(r'\d+(?:\.\d+)?', text)
    return match.group() if match else ""

def extract_choice(text: str) -> str:
    """Extract multiple choice answer."""
    import re
    match = re.search(r'\b([A-D])\b', text.upper())
    return match.group(1) if match else ""
```

## Error Handling

Handle evaluation errors gracefully:

```python
@evaluator(metrics=accuracy())
def robust_evaluator(response: str, expected: str) -> bool:
    """Evaluator with error handling."""
    try:
        # Attempt complex evaluation logic
        processed_response = preprocess_response(response)
        processed_expected = preprocess_response(expected)
        return semantic_similarity(processed_response, processed_expected) > 0.8
    except Exception as e:
        # Log error and fall back to simple comparison
        print(f"Evaluation error: {e}")
        return response.lower().strip() == expected.lower().strip()

def preprocess_response(text: str) -> str:
    """Preprocess text for evaluation."""
    # Remove extra whitespace, normalize case, etc.
    return text.strip().lower()

def semantic_similarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity score."""
    # This would typically use embeddings or other NLP techniques
    # Simplified for demonstration
    common_words = set(text1.split()) & set(text2.split())
    total_words = set(text1.split()) | set(text2.split())
    return len(common_words) / len(total_words) if total_words else 0.0
```
