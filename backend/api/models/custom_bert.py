from transformers import PreTrainedModel, AutoModel, AutoConfig
import torch
import torch.nn as nn

class CustomModel(PreTrainedModel):
    config_class = AutoConfig
    base_model_prefix = "bert"
    
    def __init__(self, config):
        super().__init__(config)
        self.bert = AutoModel.from_config(config)
        self.fc = nn.Linear(config.hidden_size, config.num_labels)
        
    def forward(self, **inputs):
        outputs = self.bert(**inputs)
        last_hidden_states = outputs.last_hidden_state
        attentions = outputs.attentions
        
        # pooled sentence representation
        feature = last_hidden_states[:, 0, :]  # only considering [CLS] token representations
        
        output = self.fc(feature)

        return output, attentions

    def _init_weights(self, module):
        """Initialize the weights"""
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0) 