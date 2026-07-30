from datasets import load_dataset
try:
    ds = load_dataset('Coder-Dragon/Indian-IPO-2006-2025')
    print(ds['train'].column_names)
    print(ds['train'][0])
except Exception as e:
    print(e)
