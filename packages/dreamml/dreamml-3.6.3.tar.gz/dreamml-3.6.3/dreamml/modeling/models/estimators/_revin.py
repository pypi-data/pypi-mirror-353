import torch
import torch.nn as nn


class RevIN(nn.Module):
    """Reversible Instance Normalization module.

    This module performs reversible instance normalization, allowing for normalization
    and denormalization of input data. It supports learnable affine parameters for scaling
    and shifting the normalized data.

    Attributes:
        num_features (int): The number of features or channels.
        eps (float): A value added for numerical stability.
        affine (bool): If True, RevIN has learnable affine parameters.
        device (str): The device on which the parameters are allocated.
    """

    def __init__(self, num_features: int, eps=1e-5, affine=True, device="cpu"):
        """Initialize the RevIN module.

        Args:
            num_features (int): The number of features or channels.
            eps (float, optional): A value added for numerical stability. Defaults to 1e-5.
            affine (bool, optional): If True, RevIN has learnable affine parameters. Defaults to True.
            device (str, optional): The device on which parameters are allocated. Defaults to "cpu".
        """
        super(RevIN, self).__init__()
        self.num_features = num_features
        self.eps = eps
        self.affine = affine
        self.device = device
        if self.affine:
            self._init_params()

    def forward(self, x, mode: str):
        """Forward pass for the RevIN module.

        Depending on the mode, the input tensor is either normalized or denormalized.

        Args:
            x (torch.Tensor): The input tensor to be normalized or denormalized.
            mode (str): Operation mode, either "norm" for normalization or "denorm" for denormalization.

        Returns:
            torch.Tensor: The normalized or denormalized tensor.

        Raises:
            NotImplementedError: If the mode is not "norm" or "denorm".
        """
        if mode == "norm":
            self._get_statistics(x)
            x = self._normalize(x)
        elif mode == "denorm":
            x = self._denormalize(x)
        else:
            raise NotImplementedError
        return x

    def _init_params(self):
        """Initialize learnable affine parameters.

        Creates and initializes the affine weight and bias parameters if affine is enabled.
        """
        self.affine_weight = nn.Parameter(torch.ones(self.num_features)).to(self.device)
        self.affine_bias = nn.Parameter(torch.zeros(self.num_features)).to(self.device)

    def _get_statistics(self, x):
        """Compute mean and standard deviation of the input tensor.

        Calculates the mean and standard deviation across all dimensions except the last one
        and detaches them from the computation graph.

        Args:
            x (torch.Tensor): The input tensor from which statistics are computed.
        """
        dim2reduce = tuple(range(1, x.ndim - 1))
        self.mean = torch.mean(x, dim=dim2reduce, keepdim=True).detach().to(self.device)
        self.stdev = (
            torch.sqrt(
                torch.var(x, dim=dim2reduce, keepdim=True, unbiased=False) + self.eps
            )
            .detach()
            .to(self.device)
        )

    def _normalize(self, x):
        """Normalize the input tensor using the computed statistics.

        Applies normalization by subtracting the mean and dividing by the standard deviation.
        If affine parameters are enabled, scales and shifts the normalized tensor accordingly.

        Args:
            x (torch.Tensor): The input tensor to be normalized.

        Returns:
            torch.Tensor: The normalized (and possibly affine-transformed) tensor.
        """
        x = x - self.mean
        x = x / self.stdev
        if self.affine:
            x = x * self.affine_weight.to(self.device)
            x = x + self.affine_bias.to(self.device)
        return x

    def _denormalize(self, x):
        """Denormalize the input tensor using the stored statistics.

        Reverses the normalization process by scaling and shifting the tensor.
        If affine parameters are enabled, adjusts the tensor using the affine weights and biases.

        Args:
            x (torch.Tensor): The input tensor to be denormalized.

        Returns:
            torch.Tensor: The denormalized tensor.
        """
        if self.affine:
            x = x - self.affine_bias.to(self.device)
            x = x / (self.affine_weight + self.eps * self.eps)
        x = x * self.stdev
        x = x + self.mean
        return x