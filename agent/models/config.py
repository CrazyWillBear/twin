"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from agent.models.Groq import qwen, oss_120b
from agent.models.OpenAI import gpt_5_1

MODEL_CONFIG = {
    "review": oss_120b,
    "summarize": qwen
}