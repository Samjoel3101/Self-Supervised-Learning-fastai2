# AUTOGENERATED! DO NOT EDIT! File to edit: 04_utils.ipynb (unless otherwise specified).

__all__ = ['Encoding', 'make_encoder', 'DropLastBatchCallback']

# Cell
from .imports import *

# Cell
class Encoding:
  def __init__(self, encoder, size = (128, 128)):
    self.sizes = model_sizes(encoder, size)
    self.idxs = unet._get_sz_change_idxs(self.sizes)

  @property
  def final_channel(self):
    return self.sizes[-1][1]

  @property
  def num_encodings(self):
    return len(self.idxs)

  def cut_idx_for_grid_size(self, grid_thresh = 12):
    idxs = []; size = []
    for idx, model_size in enumerate(self.sizes):
      assert model_size[-2] == model_size[-1], "Rectangular image is feeded"
      grid_size = model_size[-2]
      if grid_size < grid_thresh:
        break
      idxs.append(idx); size.append(model_size[-1])
    return idxs[-1] + 1, size[-1]

  def get_hooks_for_encoding(self):
    encodings = hook_outputs([model[i] for i in idxs], detach = False)
    return encodings

# Cell
def make_encoder(arch, grid_size = 12, im_size = 224):
  sample_model = create_body(arch)
  enc = Encoding(sample_model, size = (im_size, im_size))
  cut_idx, size = enc.cut_idx_for_grid_size(grid_size)
  print(f'Cut index : {cut_idx}; Size of last Grid Size: {size}')
  actual_model = create_body(arch, cut = cut_idx)
  del sample_model; del enc
  return actual_model, Encoding(actual_model, (im_size, im_size))

# Cell
class DropLastBatchCallback(Callback):
  def before_batch(self):
    if self.n_iter - 1 == self.iter:
      raise CancelBatchException()