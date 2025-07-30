import torch
from torch import nn

class GroupedQueryAttention(nn.Module):
    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        num_groups: int,
        dropout: float = 0.0,
        bias: bool = True,
        batch_first: bool = True,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        assert num_heads % num_groups == 0, "num_heads must be divisible by num_groups"
        assert num_heads > num_groups, "num_heads must be greater than num_groups"
        assert num_groups > 0, "num_groups must be greater than 0"
        head_dim = embed_dim // num_heads
        self.attention = nn.MultiheadAttention(
            embed_dim=embed_dim,
            num_heads=num_heads,
            dropout=dropout,
            bias=bias,
            batch_first=batch_first,
            kdim=head_dim * num_groups,  # Key dimension is scaled by number of groups
            vdim=head_dim * num_groups,   # Value dimension is scaled by number of groups
            batch_first=batch_first
        )