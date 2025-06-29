from app.memory.base import BaseMemory


class SimpleMemory(BaseMemory):
    contexts: list[dict[str, str]]=[]
    max_context_size: int = 10
    def __init__(self,max_size = 10):
        super().__init__()
        self.max_context_size = max_size
    def set_context(self,ctx):
        self.contexts.extend(ctx)
    def get_context(self):
        idx = len(self.contexts) - self.max_context_size
        if idx < 0:
            idx = 0
        return self.contexts[idx:]
    