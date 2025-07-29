import logging
import os

import numpy as np
import torch

from .modeling import mask_fn, get_jacobian

logger = logging.getLogger(__name__)

class basic_optimizer(torch.optim.Optimizer):
    """Base class for my optimizers that includes parameter access and setting utilities"""

    # @torch.no_grad()
    def _get_flat_params(self):
        return torch.cat([torch.cat([p.flatten() for p in param_group["params"]]) for param_group in self.param_groups])

    # @torch.no_grad()
    def _get_flat_grads(self):
        return torch.cat(
            [torch.cat([p.grad.flatten() for p in param_group["params"]]) for param_group in self.param_groups]
        )

    # def _multidimensional_backprop(self, backpropagated_tensor):
    #     """Backpropagate through a multidimensional output tensor.
    #     Args:
    #         out: multidimensional output tensor
    #         retain_graph: whether to retain the computation graph
    #     Returns:
    #         torch.Tensor: (n_out, p_param) tensor of gradients
    #     """
    #     # TODO refactor for batched operations
    #     n_out = backpropagated_tensor.numel()
    #     params = self._get_flat_params()
    #     n_params = params.numel()
    #     partial_grads = torch.zeros(n_out, n_params)
    #     backpropagated_tensor = backpropagated_tensor.flatten()
    #     for i in range(n_out):
    #         self.zero_grad()
    #         partial_mask = torch.zeros(n_out)
    #         partial_mask[i] = 1
    #         torch.autograd.backward(backpropagated_tensor, grad_tensors=partial_mask, retain_graph=True, create_graph=True)
    #         partial_grads[i] = self._get_flat_grads()
    #     return partial_grads

    # # TODO: refactor to include vectorized, functional operations for multi-dimensional outputs

    # @torch.no_grad()
    def _set_flat_params(self, flat_params):
        idx = 0
        for param_group in self.param_groups:
            for p in param_group["params"]:
                numel = p.numel()
                p.data = flat_params[idx : idx + numel].reshape_as(p)
                idx += numel
        return
    # TODO: add save optimizer/parameter state to file function to BasicOptimizer
    # logic: have a dictionary of saved parameters for each optimizer

class maskedAdam(torch.optim.Adam, basic_optimizer):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0, amsgrad=False, mask=None, mask_fn_thresh=None,
    mask_fn_quantile_thresh=None):
        super(maskedAdam, self).__init__(params, lr, betas, eps, weight_decay, amsgrad)
        self.mask = mask
        self.mask_fn_thresh = mask_fn_thresh
        self.mask_fn_quantile_thresh = mask_fn_quantile_thresh
        return

    def masked_step(self, mask=None, grad_thresh=None, grad_quantile=None, closure=None):
        """Only updates selected parameters defined by the mask or gradient threshold."""
        # either mask or grad_thresh must be provided
        # assert mask is not None or grad_thresh is not None, "Either mask or grad_thresh must be provided."

        # get the pre-step parameters and gradients
        pre_step_params = self._get_flat_params()
        # set mask.
        # mask arg has prescedence otherwise grad_thresh and grad_quantile
        if mask is None:
            mask = mask_fn(
                self._get_flat_grads(),
                thresh=self.mask_fn_thresh if grad_thresh is None else grad_thresh,
                quantile_thresh=self.mask_fn_quantile_thresh if grad_quantile is None else grad_quantile
            )

        # normal step
        super(maskedAdam, self).step(closure=closure)

        # revert the parameters for parameters UNMASKED or BELOW GRADIENT THRESHOLD
        post_step_params = self._get_flat_params()
        post_step_params[~mask] = pre_step_params[~mask]
        self._set_flat_params(post_step_params)
        return (mask).sum().item()


class maskedSGD(torch.optim.SGD, basic_optimizer):
    def __init__(self, params, lr=1e-3, momentum=0, dampening=0, weight_decay=0, nesterov=False, mask=None):
        super(maskedSGD, self).__init__(params, lr, momentum, dampening, weight_decay, nesterov)
        self.mask = mask
        return

    def masked_step(self, mask=None, grad_thresh=None, closure=None):
        """Only updates selected parameters defined by the mask or gradient threshold."""
        # either mask or grad_thresh must be provided
        assert mask is not None or grad_thresh is not None, "Either mask or grad_thresh must be provided."

        # get the pre-step parameters and gradients
        pre_step_params = self._get_flat_params()
        if mask is None:
            pre_step_grads = self._get_flat_grads()
            mask = pre_step_grads.abs() > grad_thresh

        # normal step
        super(maskedSGD, self).step(closure=closure)

        # revert the parameters for parameters UNMASKED or BELOW GRADIENT THRESHOLD
        post_step_params = self._get_flat_params()
        post_step_params[~mask] = pre_step_params[~mask]
        self._set_flat_params(post_step_params)
        return (mask).sum().item()


class SEKF(basic_optimizer):
    """Subset Extended Kalman Filter optimizer.
    ...
    IMPORTANT NOTE: This optimizer requires the gradient to be computed wrt the output of the model, NOT the loss.

    Generally lr and q are adjusted while leaving p0 at 100 for sigmoid activations and 1000 for linear activations.

    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups
        lr (float, optional): learning rate (default: 1e-3)
        q (float, optional): process noise (default: 1e-1) P&F recommend 0 for no noise up to 0.1. Generally annealed from large value to value on the order of 1e-6. This annealing helps convergence and by keeping non-zero helps avoid divergence of error covariance update
        p0 (float, optional): initial covariance matrix diagonal values (default: 1e-1)  P&F recommend 100 for sigmoid and 1,000 for linear activations
    """

    def __init__(
        self,
        params,
        lr: float = 1e-3,  # initial learning rate
        q: float = 1e-1,  # process noise
        p0: float = 100,  # initial error covariance
        mask_fn_thresh=None,
        mask_fn_quantile_thresh=None,
        save_path=None
    ):
        if not 0.0 <= lr:
            raise ValueError(f"Invalid learning rate: {lr}")
        self.mask_fn = lambda x: mask_fn(x, thresh=mask_fn_thresh, quantile_thresh=mask_fn_quantile_thresh)
        self.learning_rate = lr
        # defaults = dict(lr=lr)
        defaults = dict()
        super(SEKF, self).__init__(params, defaults)
        self._init_SEKF(p0, q)
        self.save_path = save_path
        if self.save_path is not None:
            if os.path.exists(self.save_path):
                logger.debug(f"Loading SEKF parameters from {self.save_path}")
                self.load_params(self.save_path)
            else:
                logger.debug(f"{self.save_path} does not exist, initializing SEKF parameters")
                self.save_params(self.save_path)
        return

    def _init_SEKF(self, p0, q):
        """Initialize the SEKF P, Q matrices."""
        self.n_param_elements = sum(sum(p.numel() for p in param_group["params"]) for param_group in self.param_groups)
        self.P = torch.eye(self.n_param_elements) * p0
        self.Q = torch.eye(self.n_param_elements) * q
        self.W = self._get_flat_params()
        return

    @torch.no_grad()
    def step(self, e, J, mask=None, verbose=False):
        """Performs a single optimization step.
        ARGS:
            e (torch.Tensor): (N_out) (N_out*N_stream) innovation, y_true - y_pred
            J (torch.Tensor): (N_out, N_params) Jacobian dy/dW change in *output* wrt parameters
            mask (torch.Tensor): (N_params) mask of which parameters to update
            verbose: (bool) whether to return additional information
        Returns:
            None or dict: additional information if verbose=True

        Other Notes:
            P (N_param, N_param) is the error covariance matrix
            A (N_out, N_out) is the scaling matrix
            K (N_param, N_out) is the Kalman gain

            @torch.no_grad() is used to prevent the computation graph from being stored
        """
        # parse inputs and initialize matricies
        if mask is None:
            mask = torch.ones(J.shape[1], dtype=torch.bool)
        else:
            assert mask.shape == (J.shape[1],), (
                f"Mask must have the same number of elements as the number of parameters, received {mask.shape[0]} expected {J.shape[1]}"
            )
        e = e.reshape(-1, 1)

        A0 = torch.eye(J.shape[0]) / self.learning_rate + J[:, mask] @ self.P[mask][:, mask] @ J[:, mask].T
        A = torch.linalg.solve(A0, torch.eye(J.shape[0]))
        # A = torch.linalg.inv(
        #     # learning rate injects uniform addition to main diagonal
        #     torch.eye(J.shape[0]) / self.learning_rate  # JPJ^T is the covariance of the innovation
        #     + J[:,mask] @ self.P[mask][:,mask] @ J[:,mask].T
        # )
        self.K = self.P[mask][:, mask] @ J[:, mask].T @ A
        self.dW = (self.K @ e).reshape(-1)
        # self.dP = self.K @ J[:,mask] @ self.P[mask][:,mask]
        self.W[mask] = self.W[mask] + self.dW
        # self.P[mask][:,mask] = self.P[mask][:,mask] + self.dP
        # self.P[mask][:,mask] = (torch.eye(self.n_param_elements)[mask][:,mask] - self.K @ J[:,mask]) @ self.P[mask][:,mask] + self.dP
        subset_P = (torch.eye(sum(mask)) - self.K @ J[:, mask]) @ self.P[mask][:, mask] + self.Q[mask][:, mask]
        mask_2d = mask.unsqueeze(0) & mask.unsqueeze(1)
        self.P.index_put_(torch.where(mask_2d), subset_P.flatten())
        self._set_flat_params(self.W)
        if verbose:
            return {
                "e": e,
                "J": J,
                "A": A,
                "K": self.K,
                "W": self.W,
                "P": self.P,
            }
        else:
            return

    def easy_step(self, model, x_true, y_true, loss_fn, mask_fn=None, mask=None, verbose=False):
        """
        Utility method to perform prediction, compute loss, calculate jacobian and mask, and SEKF step.
        ARGS:
            model (torch.nn.Module): model to optimize
            x_true (tuple(torch.Tensor)): input to the model
                NOTE: x_true must be a tuple of tensors, even if there is only one input to handle multi-input settings. Could change this in the future.
            y_true (torch.Tensor): target output 
            loss_fn (callable): loss function to compute the loss
            mask_fn (callable): function to compute the mask from the gradients. If not declated, or declared in initialization, assumes no mask
            mask (torch.Tensor): mask to use for the SEKF step. If not provided, will be computed from the gradients
            verbose (bool): whether to return additional information
        RETURNS:
            y_pred (torch.Tensor): predicted output
            step_info (dict, None): additional information if verbose=True, otherwise None
        """
        y_pred = model(*x_true)
        e = y_true - y_pred
        loss = loss_fn(y_pred, y_true)
        loss.backward()
        grad_loss = self._get_flat_grads()
        J = get_jacobian(model, x_true)
        if mask is None:
            if mask_fn is None:
                mask = self.mask_fn(grad_loss)
            else:
                mask = mask_fn(grad_loss)
        return y_pred, self.step(e, J, mask=mask, verbose=verbose)

    def save_params(self, path=None):
        """Saves the SEKF P and Q matrices to a npz file.
        ARGS:
            path (str): path to save the parameters to. If None, uses the save_path attribute
        RETURNS:
            None
        """
        if path is None:
            assert self.save_path is not None, "Either provide a path when calling `save_params` or set `save_path` when initializing the optimizer"
            path = self.save_path
        np.savez(path, P=self.P.numpy(), Q=self.Q.numpy())
        return

    def load_params(self, path=None):
        """Loads the SEKF P and Q matrices from a npz file.
        ARGS:
            path (str): path to load the parameters from. If None, uses the save_path attribute
        RETURNS:
            None
        """
        if path is None:
            assert self.save_path is not None, "Either provide a path when calling `load_params` or set `save_path` when initializing the optimizer"
            path = self.save_path
        data = np.load(path)
        self.P = torch.from_numpy(data["P"])
        self.Q = torch.from_numpy(data["Q"])
        return
