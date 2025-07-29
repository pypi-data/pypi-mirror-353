# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import os


def get_host_port():
    """Gets host and port from environment variables. Defaults to 0.0.0.0:8000."""
    port = int(os.environ.get("DYNAMO_PORT", 8000))
    host = os.environ.get("DYNAMO_HOST", "0.0.0.0")
    return host, port


def get_system_app_host_port():
    """Gets host and port for system app from environment variables. Defaults to choosing a random port."""
    port = int(os.environ.get("DYNAMO_SYSTEM_APP_PORT", 0))
    host = os.environ.get("DYNAMO_SYSTEM_APP_HOST", "0.0.0.0")
    return host, port
