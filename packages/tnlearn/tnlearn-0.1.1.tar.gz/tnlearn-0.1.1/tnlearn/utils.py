# Copyright 2024 Meng WANG. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import torch
from torch.utils.data import Dataset


class MyData(Dataset):
    r"""Dataset class to handle data pairs."""

    def __init__(self, pics, labels):
        self.pics = pics
        self.labels = labels

    def __getitem__(self, index):
        # Fetch a single item by index
        assert index < len(self.pics)
        return torch.Tensor(self.pics[index]), self.labels[index]

    def __len__(self):
        # Return the size of the dataset
        return len(self.pics)

    def get_tensors(self):
        # Return all images and labels as tensor batches
        return torch.Tensor([self.pics]), torch.Tensor(self.labels)
