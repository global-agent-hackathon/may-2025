| **Field**            | **Details**                                                                 |
|----------------------|------------------------------------------------------------------------------|
| **Filename**         | `youtube_video_evaluation.md`                                               |
| **Version**          | 1.0                                                                          |
| **Created**          | 2025-05-19                                                                   |
| **Status**           | ✅ Tested                                                                    |
| **Model**            | `qwen3-4b`                                                                   |
| **Temperature**      | 0.1                                                                          |
| **Top-K**            | N/A                                                                          |
| **Top-P**            | 0.9                                                                          |
| **Goal**             | Evaluate a YouTube video to determine how evident a target category is.      |
| **System Prompts**   | See prompt block below                                                       |
| **Input**            | Categories:manipulation, accuracy, indoctrination. URL:<https://www.youtube.com/watch?v=9kUvtM3txWE> |
| **Expected Output**  | See output block below                                                                   |
| **Notes**            | Prompt optimized for structured evaluation with nuanced scoring logic.       |

### 🔹 Prompts

#### Role prompt

```text
Act as a specialist in analyzing YouTube video captions with the expertise of a cross-disciplinary panel composed of experts in media literacy, communication science, psychology, journalism, and AI-based content analysis.
```

#### Goal prompt

```text
You will receive the url of a Youtube video and a list of features (labeled as categories) to evaluate with. You must analyze the video caption, evaluate the presence and its grade of certain features or categories (e.g., manipulation, veracity, ...) and indicate such a presence
```

#### Instruction prompt

```text
You will receive the url of a Youtube video and a list of features (labeled as categories) to evaluate with. Every time you receive this input, you must execute the following actions:,
    1. Get the Youtube video captions by using some of the available functions. In case of error, collect the error message. In case of success, you do not need to get the video caption again. You can use the caption to evaluate the categories defined as input.,
    2. If caption is available, analyze it carefully. The goal is to evaluate how the categories defined as input are reflected in the video. The result of this evaluation must be a numerical score (from 0 to 10) for each category.,
    If category has positive connotation (e.g., intelligence or accuracy), number 10 will the highest score you can assign to that category and 0 will be the lowest score. If feature has negative connotation (e.g., manipulation or bias), you will rank 0 as the highest score of that feature and 10 as the lowest score.
    Add your consideration about connotation (i.e., positive or negative) of each category into your results.,
    3. Calculate the overall score of all categories and a summary of the reasoning of the evaluation.
    4. Provide the final result in JSON format.

/no_think
```

#### Expected output prompt

```text
You must provide the result in JSON format. The JSON must contain the following fields:
  - categories: List of categories with the result of the evaluation. Each category must contain:
      - name: Name of the category.
      - score: Score obtained after the evaluation. If category has positive connotation (e.g., intelligence or accuracy), number 10 will the highest score you can assign to that category and 0 will be the lowest score. If feature has negative connotation (e.g., manipulation or bias), you will rank 0 as the highest score of that feature and 10 as the lowest score.
      - connotation: Connotation of the category (positive or negative).
      - reason: Reasoning of behind the score.
  - overall: Overall score and reasoning. It must contain:
      - score: Average of all categories score.
      - reason: Summary of reasons of all categories.
  - error: Error message in case of failure.
  
  Start your response with `{` and end it with `}`.
  Your output will be passed to json.loads() to convert it to a Python object. Make sure it only contains valid JSON.
  
  EXAMPLE:
  Categories:['accuracy', 'manipulation']. URL:'https://www.url.com
  After evaluating, video seems to be very accurate since the author provides specific details about his statements. Since accuracy has positive connotation and this category is clearly evident in the video, scoring will be close to 9. 
  Regarding manipulation, author claims some statements which could be seen as manipulation of public opinion.
  How manipulation has negative connotation and this category is clearly evident in the video, it will be close to 0 
  JSON Response:
  {
      "categories": [
          {
              "name": "accuracy",
              "score": 8,
              "connotation": "positive",
              "reason": "All statements are correct so score is high because of positive connotation"
          },
          {
              "name": "manipulation",
              "score": 3,
              "connotation": "negative",
              "reason": "Author tries to manipulate so the score is low because of negative connotation"
          }
      ],
      "overall": {"score": 5.5, "reason": "Summary of reasons of all categories"},
      "error": ""
  }
  
  EXAMPLE:
  Categories:['accuracy', 'manipulation']. URL:'https://www.url.com
  After evaluating, video seems to be inaccurate since the author does not provide any source that could validate his statements. Since accuracy has positive connotation and this category is not evident in the video, scoring will be close to 3.
  Regarding manipulation, author claims some statements which could be seen as manipulation of public opinion.
  How manipulation has negative connotation and this category is clearly evident in the video, it will be close to 0 
  JSON Response:
  {
      "categories": [
          {
              "name": "accuracy",
              "score": 3,
              "connotation": "positive",
              "reason": "All statements are correct so score is high because of positive connotation"
          },
          {
              "name": "manipulation",
              "score": 3,
              "connotation": "negative",
              "reason": "Author tries to manipulate so the score is low because of negative connotation"
          }
      ],
      "overall": {"score": 3, "reason": "Summary of reasons of all categories"},
      "error": ""
  }
  
  EXAMPLE:
  Categories:['accuracy', 'manipulation']. URL:'https://www.url-no-transcription.com
  Evaluation cannot be done since transcription is not available for the video. 
  JSON Response:
  {
      "categories": [],
      "overall": {score: NaN, reason: ""},
      "error": Error message from gathering process
  }
  
  EXAMPLE:
  Categories:['accuracy', 'manipulation']. URL:'https://www.url-no-transcription-language.com
  Evaluation cannot be done since transcription could not be gathered for the requested language. 
  JSON Response:
  {
      "categories": [],
      "overall": {score: NaN, reason: ""},
      "error": Error message from gathering process
  }
```

### 🔹 Output

```JSON
{
  "categories": [
    {
      "name": "accuracy",
      "score": 3,
      "connotation": "positive",
      "reason": "All statements are correct so score is high because of positive connotation"
    },
    {
      "name": "manipulation",
      "score": 3,
      "connotation": "negative",
      "reason": "Author tries to manipulate so the score is low because of negative connotation"
    }
  ],
  "overall": {
    "score": 3,
    "reason": "Summary of reasons of all categories"
  },
  "error": ""
}

```
