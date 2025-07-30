# Required libraries
import gradio as gr
import pandas as pd
import dspy
from dspy.teleprompt import (
    BootstrapFewShot, 
    BootstrapFewShotWithRandomSearch
)

# Sample DSPy optimizer setup
def prompt_optimizer(data, old_prompt, optimization_method='BootstrapFewShot', prompt_type='Predict', top_n=3, openai_model='gpt-3.5-turbo', openai_key=None):
    # Prepare data for DSPy
    examples = [dspy.Example(question=row['question'], answer=row['answer']).with_inputs('question') for _, row in data.iterrows()]

    # Initialize DSPy LM with user-provided OpenAI model and key
    lm = dspy.OpenAI(model=openai_model, api_key=openai_key)
    dspy.settings.configure(lm=lm)

    # Select Prompt type
    if prompt_type == 'Predict':
        signature = dspy.Predict('question -> answer')
    elif prompt_type == 'React':
        signature = dspy.ReAct('question -> answer')
    elif prompt_type == 'ChainOfThought':
        signature = dspy.ChainOfThought('question -> answer')

    # Choose optimization method
    if optimization_method == 'BootstrapFewShot':
        optimizer = BootstrapFewShot(metric=dspy.evaluate.answer_exact_match, max_bootstrapped_demos=top_n)
    elif optimization_method == 'BootstrapFewShotWithRandomSearch':
        optimizer = BootstrapFewShotWithRandomSearch(metric=dspy.evaluate.answer_exact_match, max_bootstrapped_demos=top_n)


    optimized_prompt = optimizer.compile(signature, trainset=examples)

    # Generate top N prompts (simplified representation)
    top_prompts = [optimized_prompt.signature for _ in range(top_n)]

    return top_prompts

# Gradio interface function
def run_promptimize(file, old_prompt, optimization_method, prompt_type, top_n, openai_model, openai_key):
    data = pd.read_excel(file.name)
    optimized_prompts = prompt_optimizer(data, old_prompt, optimization_method, prompt_type, top_n, openai_model, openai_key)

    return "\n\n---\n\n".join(optimized_prompts)

# Gradio UI
iface = gr.Interface(
    fn=run_promptimize,
    inputs=[
        gr.File(label="Upload Excel with 'question' & 'answer' columns"),
        gr.Textbox(label="Enter Old Prompt", lines=4),
        gr.Dropdown(label="Optimization Method", choices=[
            'BootstrapFewShot', 'BootstrapFewShotWithRandomSearch'
        ], value='BootstrapFewShot'),
        gr.Dropdown(label="Prompt Type", choices=['Predict', 'React', 'ChainOfThought'], value='Predict'),
        gr.Slider(minimum=1, maximum=10, value=3, step=1, label="Top N Prompts"),
        gr.Textbox(label="OpenAI Model", value='gpt-3.5-turbo'),
        gr.Textbox(label="OpenAI API Key", type="password")
    ],
    outputs=gr.Textbox(label="Optimized Prompts"),
    title="PromptVibe 🚀",
    description="Optimize your prompts easily using DSPy backend. Upload Excel (questions & answers), and get optimized prompts."
)