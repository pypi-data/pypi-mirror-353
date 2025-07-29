# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Model optimization and deployment subpackage for torch."""

import warnings as _warnings

from packaging.version import Version as _Version
from torch import __version__ as _torch_version

try:
    from . import distill, nas, opt, prune, quantization, sparsity, speculative, utils
except ImportError as e:
    raise ImportError(f"{e}\nPlease install optional ``[torch]`` dependencies.")

if _Version(_torch_version) < _Version("2.5"):
    _warnings.warn(
        "nvidia-modelopt will drop torch<2.5 support in a future release.", DeprecationWarning
    )
