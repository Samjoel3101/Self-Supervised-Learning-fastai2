# AUTOGENERATED! DO NOT EDIT! File to edit: 01_learn.ipynb (unless otherwise specified).

__all__ = ['upstream_splitter', 'SSLLearner']

# Cell
def upstream_splitter(upstream_model):
  if len(upstream_model.encoder) == 2:
    return L([upstream_model.encoder[0], upstream_model.encoder[1], upstream_model.global_rep, upstream_model.heads]).map(params)
  else:
    return L([upstream_model.encoder, upstream_model.global_rep, upstream_model.heads]).map(params)

# Cell
class SSLLearner:
  def __init__(self, upstream_learner, downstream_dls):
    self.upstream_learner = upstream_learner
    self.downstream_learner = self.create_downstream_learner(downstream_dls, upstream_learner)

  @property
  def upstr(self):
    return self.upstream_learner

  @property
  def downstr(self):
    return self.downstream_learner

  def fit(self, upstr_epochs, downstr_epochs, fit_method = ['fit', 'fit'],
          upstr_kwargs = {}, downstr_kwargs = {}):
    assert len(fit_method) == 2 ,"Specify two fit methods for two learners."
    upstr_fit = getattr(self.upstream_learner, fit_method[0])
    downstr_fit = getattr(self.downstream_learner, fit_method[1])

    upstr_fit(upstr_epochs, **upstr_kwargs)
    self.downstream_learner.freeze()
    downstr_fit(downstr_epochs, **downstr_kwargs)

  @staticmethod
  def create_downstream_learner(downstream_learner, upstream_learner):
    head = create_head(2048*2, downstream_dls.c)
    model = nn.Sequential(upstream_learner.model.encoder, head)
    def model_splitter(m):
      return L([m[0], m[1]]).map(params)
    downstream_learner = Learner(downstream_dls, model, splitter = model_splitter, metrics = [accuracy, error_rate])
    return downstream_learner