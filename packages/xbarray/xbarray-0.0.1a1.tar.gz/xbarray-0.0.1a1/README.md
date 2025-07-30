# xarray
Cross-backend Python N-dimensional array library based on Array API.

This allows you to write array transformations that can run on different backends like NumPy, PyTorch, and Jax.

## Usage:

Abstract typing:

```python
from xarray import ComputeBackend, BArrayType, BDeviceType, BDtypeType, BRNGType
from typing import Generic

class ABC(Generic[BArrayType, BDeviceType, BDtypeType, BRNGType]):
    def __init__(self, backend : ComputeBackend[BArrayType, BDeviceType, BDtypeType, BRNGType]) -> None:
        self.backend = backend

    def create_array(self) -> BArrayType:
        return self.backend.zeros(5, dtype=self.backend.default_floating_dtype)
```

Concrete usage:

```python
from xarray import pytorch as pytorch_backend

abc_pytorch_instance = ABC(pytorch_backend)
abc_pytorch_array = abc_pytorch_instance.create_array()
```