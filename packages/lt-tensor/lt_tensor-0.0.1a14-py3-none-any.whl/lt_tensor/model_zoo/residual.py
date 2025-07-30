__all__ = [
    "spectral_norm_select",
    "get_weight_norm",
    "ResBlock1D",
    "ResBlock2D",
    "ResBlock1DShuffled",
    "AdaResBlock1D",
    "ResBlocks",
]
import math
from lt_utils.common import *
import torch.nn.functional as F
from lt_tensor.torch_commons import *
from lt_tensor.model_base import Model
from lt_tensor.misc_utils import log_tensor
from lt_tensor.model_zoo.fusion import AdaFusion1D, AdaIN1D


def spectral_norm_select(module: nn.Module, enabled: bool):
    if enabled:
        return spectral_norm(module)
    return module


def get_weight_norm(norm_type: Optional[Literal["weight", "spectral"]] = None):
    if not norm_type:
        return lambda x: x
    if norm_type == "weight":
        return lambda x: weight_norm(x)
    return lambda x: spectral_norm(x)


class ConvNets(Model):
    def remove_weight_norm(self):
        for module in self.modules():
            try:
                remove_weight_norm(module)
            except ValueError:
                pass

    @staticmethod
    def init_weights(m, mean=0.0, std=0.01):
        classname = m.__class__.__name__
        if "Conv" in classname:
            m.weight.data.normal_(mean, std)


class ResBlocks(ConvNets):
    def __init__(
        self,
        channels: int,
        resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11],
        resblock_dilation_sizes: List[Union[int, List[int]]] = [
            [1, 3, 5],
            [1, 3, 5],
            [1, 3, 5],
        ],
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()
        self.num_kernels = len(resblock_kernel_sizes)
        self.rb = nn.ModuleList()
        self.activation = activation

        for k, j in zip(resblock_kernel_sizes, resblock_dilation_sizes):
            self.rb.append(ResBlock1D(channels, k, j, activation))

        self.rb.apply(self.init_weights)

    def forward(self, x: torch.Tensor):
        xs = None
        for i, block in enumerate(self.rb):
            if i == 0:
                xs = block(x)
            else:
                xs += block(x)
        x = xs / self.num_kernels
        return x



class ResBlock1D(ConvNets):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()

        self.conv_nets = nn.ModuleList(
            [
                self._get_conv_layer(i, channels, kernel_size, 1, dilation, activation)
                for i in range(3)
            ]
        )
        self.conv_nets.apply(self.init_weights)
        self.last_index = len(self.conv_nets) - 1

    def _get_conv_layer(self, id, ch, k, stride, d, actv):
        get_padding = lambda ks, d: int((ks * d - d) / 2)
        return nn.Sequential(
            actv,  # 1
            weight_norm(
                nn.Conv1d(
                    ch, ch, k, stride, dilation=d[id], padding=get_padding(k, d[id])
                )
            ),  # 2
            actv,  # 3
            weight_norm(
                nn.Conv1d(ch, ch, k, stride, dilation=1, padding=get_padding(k, 1))
            ),  # 4
        )

    def forward(self, x: Tensor):
        for cnn in self.conv_nets:
            x = cnn(x) + x
        return x


class ResBlock1DShuffled(ConvNets):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: nn.Module = nn.LeakyReLU(0.1),
        add_channel_shuffle: bool = False,  # requires pytorch 2.7.0 +
        channel_shuffle_groups=1,
    ):
        super().__init__()

        self.channel_shuffle = (
            nn.ChannelShuffle(channel_shuffle_groups)
            if add_channel_shuffle
            else nn.Identity()
        )

        self.conv_nets = nn.ModuleList(
            [
                self._get_conv_layer(i, channels, kernel_size, 1, dilation, activation)
                for i in range(3)
            ]
        )
        self.conv_nets.apply(self.init_weights)
        self.last_index = len(self.conv_nets) - 1

    def _get_conv_layer(self, id, ch, k, stride, d, actv):
        get_padding = lambda ks, d: int((ks * d - d) / 2)
        return nn.Sequential(
            actv,  # 1
            weight_norm(
                nn.Conv1d(
                    ch, ch, k, stride, dilation=d[id], padding=get_padding(k, d[id])
                )
            ),  # 2
            actv,  # 3
            weight_norm(
                nn.Conv1d(ch, ch, k, stride, dilation=1, padding=get_padding(k, 1))
            ),  # 4
        )

    def forward(self, x: Tensor):
        b = x.clone() * 0.5
        for cnn in self.conv_nets:
            x = cnn(self.channel_shuffle(x)) + b
        return x


class ResBlock2D(Model):
    def __init__(
        self,
        in_channels,
        out_channels,
        downsample=False,
    ):
        super().__init__()
        stride = 2 if downsample else 1

        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, stride, 1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(out_channels, out_channels, 3, 1, 1),
        )

        self.skip = nn.Identity()
        if downsample or in_channels != out_channels:
            self.skip = spectral_norm_select(
                nn.Conv2d(in_channels, out_channels, 1, stride)
            )
        # on less to be handled every cicle
        self.sqrt_2 = math.sqrt(2)

    def forward(self, x: Tensor):
        return (self.block(x) + self.skip(x)) / self.sqrt_2


class AdaResBlock1D(ConvNets):
    def __init__(
        self,
        res_block_channels: int,
        ada_channel_in: int,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: nn.Module = nn.LeakyReLU(0.1),
    ):
        super().__init__()

        self.conv_nets = nn.ModuleList(
            [
                self._get_conv_layer(
                    i,
                    res_block_channels,
                    ada_channel_in,
                    kernel_size,
                    1,
                    dilation,
                )
                for i in range(3)
            ]
        )
        self.conv_nets.apply(self.init_weights)
        self.last_index = len(self.conv_nets) - 1
        self.activation = activation

    def _get_conv_layer(self, id, ch, ada_ch, k, stride, d):
        get_padding = lambda ks, d: int((ks * d - d) / 2)
        return nn.ModuleDict(
            dict(
                norm1=AdaFusion1D(ada_ch, ch),
                norm2=AdaFusion1D(ada_ch, ch),
                alpha1=nn.Parameter(torch.ones(1, ada_ch, 1)),
                alpha2=nn.Parameter(torch.ones(1, ada_ch, 1)),
                conv1=weight_norm(
                    nn.Conv1d(
                        ch, ch, k, stride, dilation=d[id], padding=get_padding(k, d[id])
                    )
                ),  # 2
                conv2=weight_norm(
                    nn.Conv1d(ch, ch, k, stride, dilation=1, padding=get_padding(k, 1))
                ),  # 4
            )
        )

    def forward(self, x: torch.Tensor, y: torch.Tensor):
        for cnn in self.conv_nets:
            xt = self.activation(cnn["norm1"](x, y, cnn["alpha1"]))
            xt = cnn["conv1"](xt)
            xt = self.activation(cnn["norm2"](xt, y, cnn["alpha2"]))
            x = cnn["conv2"](xt) + x
        return x
