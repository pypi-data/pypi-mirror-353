from torch import nn

class Patchify2D(nn.Module):
    def __init__(
        self,
        patch_size: int,
        flatten_sequence: bool = True,
        *args,
        **kwargs
    ):
        """Input shape: (B, C, H, W) -> Output shape: (B, C, P, P, H/P, W/P)
        Args:
            patch_size (int): Size of the patches to extract.
            flatten_sequence (bool): If True, flattens the (P, P) to (PxP).
        """
        super().__init__(*args, **kwargs)
        self.patch_size = patch_size
        self.flatten_sequence = flatten_sequence