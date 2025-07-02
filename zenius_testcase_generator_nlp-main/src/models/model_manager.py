class ModelManager:
    def __init__(self):
        self.models = {}

    def load_model(self, model_name: str):
        if model_name not in self.models:
            # Load the model only if it's not already loaded
            from transformers import GPT2LMHeadModel, GPT2Tokenizer
            tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            model = GPT2LMHeadModel.from_pretrained(model_name)
            self.models[model_name] = {"model": model, "tokenizer": tokenizer}
        return self.models[model_name]
