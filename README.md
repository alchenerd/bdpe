# bdpe
Behavior-Driven Prompt Engineering - with self improvement suggestions

## To Start:
- Create a virtual environment and install all dependencies listed in `requirements.txt`.
- Set your OpenAI API token in the `.env` file located at `llm/tests/features/steps/`.
- In `llm/tests/features/steps/mulligan.py`, choose between `gpt-3.5-turbo` or `gpt-4`.
(Caution: The next step will generate approximately 20-30 requests for 10 scenarios, querying the OpenAI LLM.)
- Run the following command in the `llm/tests` directory:
``` bash
behave --no-capture | tee /tmp/behave_mulligan.log
```
- Check the results and improvement suggestions in `/tmp/behave_mulligan.log`.
- Search the log file for the keyword "improvement" to see the LLM's tips.

## Background
This is a small component of my ongoing side project.

I aimed to create a LangChain-OpenAI-Magic: the Gathering agent that analyzes a hand, answers a set of predefined questions, and utilizes tools to make mulligan decisions.

After creating the custom Chain-AgentExecutor amalgamation, the results were unsatisfactory.

It seemed like the prompt "Keep or Mulligan (Yes/No)?" was not sufficient.

To get quantifiable results and prompt improvement suggestions, I employed the Behave framework to outline the decision-making process of a skilled MtG player. This iterative testing process refined the prompt to its current state in the repository.

Thus, the concept of Behavior-Driven Prompt Engineering (BDPE) was born.

## What is BDPE?
Similar to Behavior-Driven Development (BDD) using the Behave framework for testing and development, BDPE treats the "prompt + LLM" combination as a random function and tests it with custom scenarios.

## What is not BDPE?
Unlike traditional BDD, BDPE cannot guarantee reproducible test results due to the inherent randomness of LLMs. This limits BDPE to providing estimations of prompt quality rather than definitive scores.

## Why BDPE?
Compared to "randomly rewriting prompts and hoping for the best," BDPE offers several advantages:
1. Systematic Testing: BDPE allows for systematic testing of the desired and undesired behaviors of the "prompt + LLM" combination.
2. Modular Code: The background, given, when, and then structure promotes reusable and modular code.
3. Identifying Regressions: BDPE can reveal issues introduced by recent prompt changes.
4. LLM-driven Improvement: The prompted LLM itself offers insights on achieving the desired output.
5. Fine-tuning or Replacement Indications: BDPE provides clear indications on when to fine-tune or replace the LLM. Hallucinations in the LLM's improvement suggestions signify its inability to pinpoint prompt elements responsible for positive or negative outcomes. This hints at a problem beyond the capacity of a refined prompt to solve.
