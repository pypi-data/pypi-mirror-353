import torch
from torch import nn

class Patchify2D(nn.Module):
    def __init__(
        self,
        patch_size: int,
        flatten_sequence: bool = True,
        *args,
        **kwargs
    ):
        """Input shape: (B, C, H, W) -> Output shape: (B, C, P*P, H/P, W/P) or (B, C, P, P, H/P, W/P)
        Args:
            patch_size (int): Size of the patches to extract.
            flatten_sequence (bool): If True, flattens the (P, P) to (P*P).
        """
        super().__init__(*args, **kwargs)
        self.patch_size = patch_size
        self.flatten_sequence = flatten_sequence

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, C, H, W = x.shape
        P = self.patch_size
        patches = x.unfold(2, P, P).unfold(3, P, P)  # (B, C, H/P, W/P, P, P)
        
        if self.flatten_sequence:
            patches = patches.reshape(B, C, H//P, W//P, P*P)
            patches = patches.permute(0, 1, 4, 2, 3)
        else:
            patches = patches.permute(0, 1, 4, 5, 2, 3)
            
        return patches