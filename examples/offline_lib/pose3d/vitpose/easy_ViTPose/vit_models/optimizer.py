import torch.optim as optim

class LayerDecayOptimizer:
    def __init__(self, optimizer, layerwise_decay_rate):
        self.optimizer = optimizer
        self.layerwise_decay_rate = layerwise_decay_rate
        self.param_groups = optimizer.param_groups
        
    def step(self, *args, **kwargs):
        for i, group in enumerate(self.optimizer.param_groups):
            group['lr'] *= self.layerwise_decay_rate[i]
        self.optimizer.step(*args, **kwargs)
        
    def zero_grad(self, *args, **kwargs):
        self.optimizer.zero_grad(*args, **kwargs)