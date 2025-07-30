# Required libraries
import os
import gradio as gr
import pandas as pd
import dspy
from dspy.teleprompt import (
    BootstrapFewShot, 
    BootstrapFewShotWithRandomSearch
)

# Accuracy evaluation
def evaluate_accuracy(module, dataset):
    correct = 0
    for ex in dataset:
        pred = module.forward(question=ex.question)
        if pred.answer.strip().lower() == ex.answer.strip().lower():
            correct += 1
    return correct / len(dataset) if dataset else 0.0

# Gradio pipeline
def run_promptimize(file, old_prompt, optimization_method, prompt_type, top_n, openai_model, openai_key):
    try:
        # Read Excel file
        df = pd.read_excel(file.name)
        examples = [dspy.Example(question=row['question'], answer=row['answer']).with_inputs('question') for _, row in df.iterrows()]

        # Configure LLM
        os.environ["OPENAI_API_KEY"] = openai_key
        lm = dspy.LM(model=openai_model)
        dspy.settings.configure(lm=lm)

        # Signature
        if prompt_type == 'Predict':
            signature = dspy.Predict('question -> answer')
        elif prompt_type == 'React':
            signature = dspy.ReAct('question -> answer')
        elif prompt_type == 'ChainOfThought':
            signature = dspy.ChainOfThought('question -> answer')
        else:
            return "❌ Invalid Prompt Type"

        # Evaluate old prompt
        class OldPromptModule(dspy.Module):
            def forward(self, question):
                response = lm(f"{old_prompt}\nquestion: {question}\nanswer:")
                return dspy.Prediction(answer=response[0].strip())

        old_module = OldPromptModule()
        old_accuracy = evaluate_accuracy(old_module, examples)

        # Optimizer
        if optimization_method == 'BootstrapFewShot':
            optimizer = BootstrapFewShot(metric=dspy.evaluate.answer_exact_match, max_bootstrapped_demos=top_n)
        elif optimization_method == 'BootstrapFewShotWithRandomSearch':
            optimizer = BootstrapFewShotWithRandomSearch(metric=dspy.evaluate.answer_exact_match, max_bootstrapped_demos=top_n)
        else:
            return "❌ Invalid Optimization Method"

        # Optimize prompt
        optimized_module = optimizer.compile(signature, trainset=examples)
        new_accuracy = evaluate_accuracy(optimized_module, examples)
        delta_accuracy = new_accuracy - old_accuracy

        result = f"""
🧠 Best Optimized Prompt:
--------------------------
{optimized_module.signature}

📊 Accuracy Comparison:
--------------------------
Old Prompt Accuracy   : {old_accuracy:.2%}
New Prompt Accuracy   : {new_accuracy:.2%}
🔼 Accuracy Improvement: {delta_accuracy:.2%}
"""
        return result.strip()
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Launch Gradio
iface = gr.Interface(
    fn=run_promptimize,
    inputs=[
        gr.File(label="📂 Upload Excel (question & answer columns)"),
        gr.Textbox(label="📝 Old Prompt", lines=5),
        gr.Dropdown(label="⚙️ Optimization Method", choices=[
            'BootstrapFewShot', 'BootstrapFewShotWithRandomSearch'
        ], value='BootstrapFewShot'),
        gr.Dropdown(label="🧠 Prompt Type", choices=['Predict', 'React', 'ChainOfThought'], value='Predict'),
        gr.Slider(minimum=1, maximum=10, value=3, step=1, label="🔢 Top N Demos"),
        gr.Textbox(label="💬 Gen AI Model", value='gpt-3.5-turbo'),
        gr.Textbox(label="🔐 OpenAI API Key", type="password")
    ],
    outputs=gr.Textbox(label="📈 Optimized Result", lines=15),
    title="PromptVibe 🚀",
    description="Optimize your prompts using DSPy + OpenAI. Upload Excel, enter old prompt, and compare results."
)