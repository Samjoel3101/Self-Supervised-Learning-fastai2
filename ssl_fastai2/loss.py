# AUTOGENERATED! DO NOT EDIT! File to edit: 02_loss.ipynb (unless otherwise specified).

__all__ = ['DotProduct', 'NTXentLoss', 'BaseSSLLoss', 'CGDLoss', 'BaseSIMClrLoss', 'SIMClrLoss']

# Cell
from .imports import *

# Cell
class DotProduct(nn.Module):
  def forward(self, x, y):
    return torch.tensordot(x.unsqueeze(1), y.T.unsqueeze(0), dims = 2)

class NTXentLoss(nn.Module): # Normalised Temperature Scaled Cross Entropy
  def __init__(self, batch_size, similarity_type = 'cosine', temp = 0.1, use_softmax = False):
    super().__init__()
    self.use_softmax = use_softmax
    self.temp = temp

    if torch.cuda.is_available():
      self.device = torch.device('cuda')
    else:
      self.device = torch.device('cpu')

    self.batch_size = batch_size
    self.neg_mask = self._get_neg_mask().to(self.device)
    self.similarity = self._get_similarity(similarity_type.lower())
    self.criterion = nn.CrossEntropyLoss(reduction = 'sum')
    if use_softmax:
      self.softmax = nn.Softmax(dim = -1)

  def _get_similarity(self, sim_type):
    if sim_type == 'cosine':
      return self.cosine_sim
    else:
      return DotProduct()

  def cosine_sim(self, x, y):
    return nn.CosineSimilarity(dim = -1)(x.unsqueeze(1), y.unsqueeze(0))

  @property
  def _T_batch(self): return 2*self.batch_size

  def _get_neg_mask(self):
    diagonal = np.eye(self._T_batch)
    upper_diag = np.eye(self._T_batch, k = self.batch_size)
    lower_diag = np.eye(self._T_batch, k = -self.batch_size)
    mask = torch.from_numpy((diagonal + upper_diag + lower_diag))
    return (1 - mask).type(torch.bool)

  def forward(self, zi, zj):
    feature_rep = torch.cat([zi, zj], dim = 0)

    similarity_matrix = self.similarity(feature_rep, feature_rep)
    similarity_matrix = similarity_matrix/self.temp

    negatives = similarity_matrix[self.neg_mask].view(self._T_batch, -1)

    l_pos = torch.diag(similarity_matrix, -self.batch_size)
    r_pos = torch.diag(similarity_matrix, self.batch_size)
    positives = torch.cat([l_pos, r_pos]).view(self._T_batch, -1)

    labels = torch.zeros(self._T_batch).to(self.device).long()
    logits = torch.cat([positives, negatives], dim = 1)
    if self.use_softmax:
      logits = self.softmax(logits)
    loss = self.criterion(logits, labels)

    return loss/self._T_batch

# Cell
class BaseSSLLoss(nn.Module):
  def __init__(self, model, with_negatives = False, global_loss_func = None, branch_loss_func = None,
               glob_loss_weight = 1., branch_loss_weight = 1.):
    super().__init__()
    self.model = model
    self.with_negatives = with_negatives
    self.glob_loss_weight = glob_loss_weight; self.branch_loss_weight = branch_loss_weight
    self.global_loss_func = global_loss_func
    if branch_loss_func:
      self.branch_loss_func = branch_loss_func

# Cell
class CGDLoss(BaseSSLLoss):
  def forward(self, *yb):
    '''Depending on Application targ could be positives or the augmentations of the same image '''

    if self.with_negatives:
      pred, targ, negatives, labels = yb
    else:
      pred, targ, labels = yb

    targ = self.model(targ, glob = False)
    if self.with_negatives:
      neg = self.model(negatives, glob = False)

    global_loss = self.glob_loss_weight * self.global_loss_func(pred[0], labels)

    if self.with_negatives:
      target_loss = self.branch_loss_weight * self.branch_loss_func(pred[1], targ, neg)

    return global_loss + target_loss

# Cell
class BaseSIMClrLoss(BaseSSLLoss):
  def forward(self, pred, targ):
    targ = self.model(targ)
    loss = self.glob_loss_weight * self.global_loss_func(pred[0], targ[0])
    return loss

def SIMClrLoss(model, batch_size, **kwargs):
  return BaseSIMClrLoss(model = model, global_loss_func = NTXentLoss(batch_size, **kwargs))