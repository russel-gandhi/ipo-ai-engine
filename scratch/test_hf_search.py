from huggingface_hub import HfApi
api = HfApi()
datasets = api.list_datasets(search="Indian IPO", limit=5)
for d in datasets:
    print(d.id)
