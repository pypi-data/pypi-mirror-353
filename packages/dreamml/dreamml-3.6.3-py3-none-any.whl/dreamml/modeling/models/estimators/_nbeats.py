import numpy as np
import torch
from torch import nn


class NBeatsNet(nn.Module):
    """N-BEATS neural network for time series forecasting.

    This network consists of multiple stacks of blocks, each designed to capture different
    aspects of the time series data such as trend and seasonality.

    Attributes:
        SEASONALITY_BLOCK (str): Identifier for seasonality block type.
        TREND_BLOCK (str): Identifier for trend block type.
        GENERIC_BLOCK (str): Identifier for generic block type.
        forecast_length (int): Number of time steps to forecast.
        backcast_length (int): Number of time steps to use for backcasting.
        hidden_layer_units (int): Number of units in hidden layers of each block.
        nb_blocks_per_stack (int): Number of blocks per stack.
        share_weights_in_stack (bool): Whether to share weights within a stack.
        nb_harmonics (int, optional): Number of harmonics for seasonality modeling.
        stack_types (tuple): Types of stacks to include in the network.
        stacks (list): List of block stacks in the network.
        thetas_dim (tuple): Dimensions of theta parameters for each stack type.
        parameters (nn.ParameterList): List of learnable parameters.
        device (torch.device): Device on which the network is located.
        _gen_intermediate_outputs (bool): Flag to generate intermediate outputs.
        _intermediary_outputs (list): List to store intermediate outputs.
        train_global_loss (list): List to store training losses.
        test_global_loss (list): List to store testing losses.
    """

    SEASONALITY_BLOCK = "seasonality"
    TREND_BLOCK = "trend"
    GENERIC_BLOCK = "generic"

    def __init__(
        self,
        device=torch.device("cpu"),
        stack_types=(TREND_BLOCK, SEASONALITY_BLOCK),
        nb_blocks_per_stack=3,
        forecast_length=5,
        backcast_length=10,
        thetas_dim=(4, 8),
        share_weights_in_stack=False,
        hidden_layer_units=256,
        nb_harmonics=None,
    ):
        """Initializes the NBeatsNet.

        Args:
            device (torch.device, optional): Device to run the network on. Defaults to CPU.
            stack_types (tuple, optional): Types of stacks to include. Defaults to (TREND_BLOCK, SEASONALITY_BLOCK).
            nb_blocks_per_stack (int, optional): Number of blocks per stack. Defaults to 3.
            forecast_length (int, optional): Length of the forecast horizon. Defaults to 5.
            backcast_length (int, optional): Length of the backcast horizon. Defaults to 10.
            thetas_dim (tuple, optional): Dimensions of theta parameters for each stack type. Defaults to (4, 8).
            share_weights_in_stack (bool, optional): Whether to share weights within a stack. Defaults to False.
            hidden_layer_units (int, optional): Number of hidden units in each block. Defaults to 256.
            nb_harmonics (int, optional): Number of harmonics for seasonality blocks. Defaults to None.
        
        Raises:
            ValueError: If an invalid stack type is provided.
        """
        super(NBeatsNet, self).__init__()
        self.forecast_length = forecast_length
        self.backcast_length = backcast_length
        self.hidden_layer_units = hidden_layer_units
        self.nb_blocks_per_stack = nb_blocks_per_stack
        self.share_weights_in_stack = share_weights_in_stack
        self.nb_harmonics = nb_harmonics
        self.stack_types = stack_types
        self.stacks = []
        self.thetas_dim = thetas_dim
        self.parameters = []
        self.device = device
        for stack_id in range(len(self.stack_types)):
            self.stacks.append(self.create_stack(stack_id))
        self.parameters = nn.ParameterList(self.parameters)
        self.to(self.device)

        self._gen_intermediate_outputs = False
        self._intermediary_outputs = []
        self.train_global_loss = []
        self.test_global_loss = []

    def create_stack(self, stack_id):
        """Creates a stack of blocks based on the stack type.

        Args:
            stack_id (int): Identifier for the stack type.

        Returns:
            list: List of blocks in the stack.
        
        Raises:
            ValueError: If an invalid stack type is encountered.
        """
        stack_type = self.stack_types[stack_id]
        blocks = []
        for block_id in range(self.nb_blocks_per_stack):
            block_init = NBeatsNet.select_block(stack_type)
            if self.share_weights_in_stack and block_id != 0:
                block = blocks[-1]
            else:
                block = block_init(
                    self.hidden_layer_units,
                    self.thetas_dim[stack_id],
                    self.device,
                    self.backcast_length,
                    self.forecast_length,
                    self.nb_harmonics,
                )
                self.parameters.extend(block.parameters())
            blocks.append(block)
        return blocks

    @staticmethod
    def select_block(block_type):
        """Selects the appropriate block class based on the block type.

        Args:
            block_type (str): Type of the block ('seasonality', 'trend', or 'generic').

        Returns:
            class: Corresponding block class.
        
        Raises:
            ValueError: If the block type is not recognized.
        """
        if block_type == NBeatsNet.SEASONALITY_BLOCK:
            return SeasonalityBlock
        elif block_type == NBeatsNet.TREND_BLOCK:
            return TrendBlock
        else:
            return GenericBlock

    def forward(self, backcast, segment):
        """Performs the forward pass of the network.

        Args:
            backcast (torch.Tensor): Input backcast tensor.
            segment (torch.Tensor): Segment tensor for conditioning.

        Returns:
            tuple:
                torch.Tensor: Updated backcast after processing.
                torch.Tensor: Forecast generated by the network.
        """
        self._intermediary_outputs = []
        backcast = squeeze_last_dim(backcast)
        segment = segment.to(self.device)
        forecast = torch.zeros(
            size=(
                backcast.size()[0],
                self.forecast_length,
            )
        )

        for stack_id in range(len(self.stacks)):
            for block_id in range(len(self.stacks[stack_id])):
                b, f = self.stacks[stack_id][block_id](backcast, segment)
                backcast = backcast.to(self.device) - b
                forecast = forecast.to(self.device) + f
                block_type = self.stacks[stack_id][block_id].__class__.__name__
                layer_name = f"stack_{stack_id}-{block_type}_{block_id}"
                if self._gen_intermediate_outputs:
                    self._intermediary_outputs.append(
                        {"value": f.detach().numpy(), "layer": layer_name}
                    )
        return backcast, forecast


def squeeze_last_dim(tensor):
    """Squeezes the last dimension of the tensor if it is of size 1.

    Args:
        tensor (torch.Tensor): Input tensor.

    Returns:
        torch.Tensor: Tensor with the last dimension squeezed if applicable.
    """
    if len(tensor.shape) == 3 and tensor.shape[-1] == 1:
        return tensor[..., 0]
    return tensor


def seasonality_model(thetas, t, device):
    """Generates seasonality component based on thetas and time.

    Args:
        thetas (torch.Tensor): Theta parameters for seasonality.
        t (torch.Tensor): Time steps.
        device (torch.device): Device to perform computations on.

    Returns:
        torch.Tensor: Seasonality component.
    
    Raises:
        AssertionError: If thetas_dim is too large.
    """
    p = thetas.size()[-1]
    assert p <= thetas.shape[1], "thetas_dim is too big."
    p1, p2 = (p // 2, p // 2) if p % 2 == 0 else (p // 2, p // 2 + 1)
    s1 = torch.tensor(np.array([np.cos(2 * np.pi * i * t) for i in range(p1)])).float()
    s2 = torch.tensor(np.array([np.sin(2 * np.pi * i * t) for i in range(p2)])).float()
    S = torch.cat([s1, s2])
    return thetas.mm(S.to(device))


def trend_model(thetas, t, device):
    """Generates trend component based on thetas and time.

    Args:
        thetas (torch.Tensor): Theta parameters for trend.
        t (torch.Tensor): Time steps.
        device (torch.device): Device to perform computations on.

    Returns:
        torch.Tensor: Trend component.
    
    Raises:
        AssertionError: If thetas_dim is too large.
    """
    p = thetas.size()[-1]
    assert p <= 4, "thetas_dim is too big."
    T = torch.tensor(np.array([t**i for i in range(p)])).float()
    return thetas.mm(T.to(device))


def linear_space(backcast_length, forecast_length, is_forecast=True):
    """Generates a linear space for time steps.

    Args:
        backcast_length (int): Length of the backcast horizon.
        forecast_length (int): Length of the forecast horizon.
        is_forecast (bool, optional): Whether to generate space for forecasting. Defaults to True.

    Returns:
        numpy.ndarray: Generated linear space.
    """
    horizon = forecast_length if is_forecast else backcast_length
    return np.arange(0, horizon) / horizon


class Block(nn.Module):
    """Base class for different types of blocks in the N-BEATS network.

    Each block consists of fully connected layers and produces theta parameters
    for generating backcast and forecast components.

    Attributes:
        units (int): Number of units in hidden layers.
        thetas_dim (int): Dimension of theta parameters.
        backcast_length (int): Length of the backcast horizon.
        forecast_length (int): Length of the forecast horizon.
        share_thetas (bool): Whether to share theta parameters.
        dropout (nn.Dropout): Dropout layer for regularization.
        segment_dim (int): Dimension of the segment input.
        fc1 (nn.Linear): First fully connected layer.
        fc2 (nn.Linear): Second fully connected layer.
        fc3 (nn.Linear): Third fully connected layer.
        fc4 (nn.Linear): Fourth fully connected layer.
        device (torch.device): Device to perform computations on.
        backcast_linspace (numpy.ndarray): Linspace for backcast.
        forecast_linspace (numpy.ndarray): Linspace for forecast.
        theta_b_fc (nn.Linear): Fully connected layer for backcast theta.
        theta_f_fc (nn.Linear): Fully connected layer for forecast theta.
    """

    def __init__(
        self,
        units,
        thetas_dim,
        device,
        backcast_length=10,
        forecast_length=5,
        share_thetas=False,
        nb_harmonics=None,
        segment_dim=1,
    ):
        """Initializes the Block.

        Args:
            units (int): Number of units in hidden layers.
            thetas_dim (int): Dimension of theta parameters.
            device (torch.device): Device to perform computations on.
            backcast_length (int, optional): Length of the backcast horizon. Defaults to 10.
            forecast_length (int, optional): Length of the forecast horizon. Defaults to 5.
            share_thetas (bool, optional): Whether to share theta parameters. Defaults to False.
            nb_harmonics (int, optional): Number of harmonics (if applicable). Defaults to None.
            segment_dim (int, optional): Dimension of the segment input. Defaults to 1.
        """
        super(Block, self).__init__()
        self.units = units
        self.thetas_dim = thetas_dim
        self.backcast_length = backcast_length
        self.forecast_length = forecast_length
        self.share_thetas = share_thetas
        self.dropout = nn.Dropout(p=0.2)

        self.segment_dim = segment_dim

        self.fc1 = nn.Linear(backcast_length + segment_dim, units)
        self.fc2 = nn.Linear(units, units)
        self.fc3 = nn.Linear(units, units)
        self.fc4 = nn.Linear(units, units)

        self.device = device
        self.backcast_linspace = linear_space(
            backcast_length, forecast_length, is_forecast=False
        )
        self.forecast_linspace = linear_space(
            backcast_length, forecast_length, is_forecast=True
        )
        if share_thetas:
            self.theta_f_fc = self.theta_b_fc = nn.Linear(units, thetas_dim, bias=False)
        else:
            self.theta_b_fc = nn.Linear(units, thetas_dim, bias=False)
            self.theta_f_fc = nn.Linear(units, thetas_dim, bias=False)

    def forward(self, x, segment):
        """Performs the forward pass of the block.

        Args:
            x (torch.Tensor): Input tensor for backcast.
            segment (torch.Tensor): Segment tensor for conditioning.

        Returns:
            torch.Tensor: Output tensor after processing.
        """
        x = squeeze_last_dim(x)
        x = torch.cat([x, segment], dim=-1)

        x = self.fc1(x.to(self.device))
        x = torch.relu(x)
        x = self.dropout(x)

        x = self.fc2(x.to(self.device))
        x = torch.relu(x)
        x = self.dropout(x)

        x = self.fc3(x.to(self.device))
        x = torch.relu(x)
        x = self.dropout(x)

        x = self.fc4(x.to(self.device))
        x = torch.relu(x)
        return x

    def __str__(self):
        """Returns a string representation of the block.

        Returns:
            str: String describing the block configuration.
        """
        block_type = type(self).__name__
        return (
            f"{block_type}(units={self.units}, thetas_dim={self.thetas_dim}, "
            f"backcast_length={self.backcast_length}, forecast_length={self.forecast_length}, "
            f"share_thetas={self.share_thetas}"
        )


class SeasonalityBlock(Block):
    """Block specialized for modeling seasonality in the time series.

    Inherits from the base Block class and utilizes the seasonality_model to generate
    backcast and forecast components.

    Attributes:
        nb_harmonics (int, optional): Number of harmonics for seasonality. Defaults to None.
    """

    def __init__(
        self,
        units,
        thetas_dim,
        device,
        backcast_length=10,
        forecast_length=5,
        nb_harmonics=None,
        segment_dim=1,
    ):
        """Initializes the SeasonalityBlock.

        Args:
            units (int): Number of units in hidden layers.
            thetas_dim (int): Dimension of theta parameters.
            device (torch.device): Device to perform computations on.
            backcast_length (int, optional): Length of the backcast horizon. Defaults to 10.
            forecast_length (int, optional): Length of the forecast horizon. Defaults to 5.
            nb_harmonics (int, optional): Number of harmonics for seasonality. Defaults to None.
            segment_dim (int, optional): Dimension of the segment input. Defaults to 1.
        """
        if nb_harmonics:
            super(SeasonalityBlock, self).__init__(
                units,
                nb_harmonics,
                device,
                backcast_length,
                forecast_length,
                share_thetas=True,
                segment_dim=segment_dim,
            )
        else:
            super(SeasonalityBlock, self).__init__(
                units,
                forecast_length,
                device,
                backcast_length,
                forecast_length,
                share_thetas=True,
                segment_dim=segment_dim,
            )

    def forward(self, x, segment):
        """Performs the forward pass of the SeasonalityBlock.

        Args:
            x (torch.Tensor): Input tensor for backcast.
            segment (torch.Tensor): Segment tensor for conditioning.

        Returns:
            tuple:
                torch.Tensor: Seasonality backcast component.
                torch.Tensor: Seasonality forecast component.
        """
        x = super(SeasonalityBlock, self).forward(x, segment)
        backcast = seasonality_model(
            self.theta_b_fc(x), self.backcast_linspace, self.device
        )
        forecast = seasonality_model(
            self.theta_f_fc(x), self.forecast_linspace, self.device
        )
        return backcast, forecast


class TrendBlock(Block):
    """Block specialized for modeling trend in the time series.

    Inherits from the base Block class and utilizes the trend_model to generate
    backcast and forecast components.
    """

    def __init__(
        self,
        units,
        thetas_dim,
        device,
        backcast_length=10,
        forecast_length=5,
        nb_harmonics=None,
        segment_dim=1,
    ):
        """Initializes the TrendBlock.

        Args:
            units (int): Number of units in hidden layers.
            thetas_dim (int): Dimension of theta parameters.
            device (torch.device): Device to perform computations on.
            backcast_length (int, optional): Length of the backcast horizon. Defaults to 10.
            forecast_length (int, optional): Length of the forecast horizon. Defaults to 5.
            nb_harmonics (int, optional): Number of harmonics (not used). Defaults to None.
            segment_dim (int, optional): Dimension of the segment input. Defaults to 1.
        """
        super(TrendBlock, self).__init__(
            units,
            thetas_dim,
            device,
            backcast_length,
            forecast_length,
            share_thetas=True,
            segment_dim=segment_dim,
        )

    def forward(self, x, segment):
        """Performs the forward pass of the TrendBlock.

        Args:
            x (torch.Tensor): Input tensor for backcast.
            segment (torch.Tensor): Segment tensor for conditioning.

        Returns:
            tuple:
                torch.Tensor: Trend backcast component.
                torch.Tensor: Trend forecast component.
        """
        x = super(TrendBlock, self).forward(x, segment)
        backcast = trend_model(self.theta_b_fc(x), self.backcast_linspace, self.device)
        forecast = trend_model(self.theta_f_fc(x), self.forecast_linspace, self.device)
        return backcast, forecast


class GenericBlock(Block):
    """Generic block for N-BEATS that can model any component of the time series.

    Inherits from the base Block class and adds linear layers to generate
    backcast and forecast directly from theta parameters.
    """

    def __init__(
        self,
        units,
        thetas_dim,
        device,
        backcast_length,
        forecast_length,
        nb_harmonics=None,
        segment_dim=1,
    ):
        """Initializes the GenericBlock.

        Args:
            units (int): Number of units in hidden layers.
            thetas_dim (int): Dimension of theta parameters.
            device (torch.device): Device to perform computations on.
            backcast_length (int): Length of the backcast horizon.
            forecast_length (int): Length of the forecast horizon.
            nb_harmonics (int, optional): Number of harmonics (not used). Defaults to None.
            segment_dim (int, optional): Dimension of the segment input. Defaults to 1.
        """
        super(GenericBlock, self).__init__(
            units,
            thetas_dim,
            device,
            backcast_length,
            forecast_length,
            segment_dim=segment_dim,
        )

        self.backcast_fc = nn.Linear(thetas_dim, backcast_length)
        self.forecast_fc = nn.Linear(thetas_dim, forecast_length)

    def forward(self, x):
        """Performs the forward pass of the GenericBlock.

        Args:
            x (torch.Tensor): Input tensor for backcast.

        Returns:
            tuple:
                torch.Tensor: Generic backcast component.
                torch.Tensor: Generic forecast component.
        """
        x = super(GenericBlock, self).forward(x)

        theta_b = self.theta_b_fc(x)
        theta_f = self.theta_f_fc(x)

        backcast = self.backcast_fc(theta_b)
        forecast = self.forecast_fc(theta_f)

        return backcast, forecast