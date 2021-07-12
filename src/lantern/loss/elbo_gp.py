import attr
import torch
from torch.nn import functional as F
from torch.distributions.kl import kl_divergence
from torch.distributions import Gamma, Normal
from torch import nn
from gpytorch.likelihoods import GaussianLikelihood
from gpytorch.likelihoods import MultitaskGaussianLikelihood
from gpytorch.mlls import VariationalELBO

from lantern.loss import Term


@attr.s(eq=False)
class ELBO_GP(Term):

    """The variational ELBO objective for GPs
    """

    mll = attr.ib(repr=False)

    def loss(self, yhat, y, noise=None, *args, **kwargs) -> dict:
        ll, kl, log_prior = self.mll(yhat, y, noise=noise)

        return {
            "neg-loglikelihood": -ll,
            "gp-kl": kl,
            "neg-log-gp-prior": -log_prior,
        }

    @classmethod
    def fromModel(
        cls, model, N, objective=VariationalELBO,
    ):
        return cls(
            objective(model.likelihood, model.surface, num_data=N, combine_terms=False),
        )
