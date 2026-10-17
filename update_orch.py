with open('quant_engine/orchestrator.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("execution = evaluate_execution(trigger, context, technicals)", "execution = evaluate_execution(trigger, context, technicals, llm_analysis, nse_data)")
with open('quant_engine/orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Updated orchestrator.py')
