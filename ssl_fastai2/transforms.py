# AUTOGENERATED! DO NOT EDIT! File to edit: 05_transforms.ipynb (unless otherwise specified).

__all__ = ['TensorSSLImage', 'SSLImage', 'SSLTransform']

# Cell
from .imports import *

# Cell
class TensorSSLImage(TensorImage): pass
class SSLImage(PILImage):
  _tensor_cls = TensorSSLImage

class SSLTransform(Transform):
  order = 25
  def __init__(self, augmentations = [Rotate(p = 1.), Flip(p = 1.), Dihedral(p = 1.), Warp(0.2, p = 1.),
                                      Brightness(0.5, p = 1.), Saturation(0.5, p = 1.)]):
    store_attr(self, 'augmentations')

  def encodes(self, x:TensorSSLImage):
    x = IntToFloatTensor(div = 1.)(x)
    for i in range(len(self.augmentations)):
      aug = random.choice(self.augmentations)
      x = aug(x)
      x = TensorImage(x)
    return x