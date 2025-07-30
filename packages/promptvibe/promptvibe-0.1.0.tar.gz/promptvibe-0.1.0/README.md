# 🚀 PromptVibe

**PromptVibe** is a lightweight Gradio-powered UI tool that helps you **optimize LLM prompts** using [DSPy](https://github.com/stanford-crfm/dspy) as the backend. Just upload your golden dataset (questions and answers in Excel), provide your current prompt, and select the optimization technique — PromptVibe will generate top N optimized prompts based on evaluation metrics.

---

## 🌟 Features

- 🔄 Upload Excel dataset with `question` and `answer` columns
- 🧠 Choose from multiple prompt types: `Predict`, `ReAct`, or `ChainOfThought`
- 🛠️ Optimize using DSPy methods:
  - `BootstrapFewShot`
  - `BootstrapFewShotWithRandomSearch`
- 🎯 Get top-N optimized prompts using answer exact match metric
- 🔐 Secure API key entry for OpenAI models

---

## 🧩 How It Works

1. Upload an Excel file with `question` and `answer` columns.
2. Enter your existing ("old") prompt.
3. Choose optimization method and prompt type.
4. Enter the number of top prompts to retrieve.
5. Provide your OpenAI model name (e.g., `gpt-3.5-turbo`) and API key.
6. View the optimized prompts generated using DSPy’s optimization engine.

---

## 📁 Excel File Format

Your Excel file must contain the following columns:

| question               | answer                |
|------------------------|------------------------|
| What is AI?            | AI is Artificial Intelligence. |
| How does GPT work?     | GPT uses transformer architecture. |

---

## 🛠️ Installation

```bash
python -m venv venv 

pip install PromptVibe 

promptvibe

```


