from __future__ import annotations
from typing import (
    Any,
    Optional,
    List,
    Dict,
    Union,
)
import healpy as hp
import pyccl as ccl


class Mock:
    @staticmethod
    def generate_full_batch(
        nside: int,
        batch_size: int = 1,
        mask_type: str = "decals",
        add_noise: bool = True,
        add_mask: bool = True,
        add_edge: bool = True,
        rotate: bool = False,
        shape_noise_sigma: float = 0.4,
        galaxy_density: float = 30.0,
        iterN: int = 16,
        seed: Optional[int] = None,
        data_source: str = "val",
        return_type: str = "numpy",
    ) -> Dict[str, Any]:
        pass
