from .LLM import LLM
from .Tools import *

class Annotator(LLM):
    def __init__(self, prompt, labels, model_name="llama3-8b-8192", token=None):
        super().__init__(model_name, token)
        
        self.prompt = prompt
        self.labels = labels
    
    def truncate_to_5000_words(self, text):
        try:
            cleaned_text = ' '.join(text.split())
            words = cleaned_text.split()
            return ' '.join(words[:5000]) if len(words) > 5000 else cleaned_text
        
        except Exception as e:
            return ''
    def annotate(self, text):
        text = self.truncate_to_5000_words(text)
        input_prompt = [
            {"role": "user", "content": self.prompt},
            {"role": "user", "content": text},
        ]
        
        try:
            ans = self.llm.invoke(input_prompt)
            print("ans", ans)
            ans = trim_text(ans)
            print("trimmed ans",ans)
            label = extract_label(ans, labels=self.labels)
            print("label", label)
            if label:
                reasoning = extract_reasoning(ans)
                return label, reasoning
            
            return label, None        
        
        except Exception as e:
            
            print(f"Error querying model: {e}")
            return None, None
