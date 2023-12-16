from typing import Optional
import gradio

import nativedancer.globals
import nativedancer.choices
from nativedancer import helperdoc

MAX_MEMORY_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global MAX_MEMORY_SLIDER

	MAX_MEMORY_SLIDER = gradio.Slider(
		label = helperdoc.get('max_memory_slider_label'),
		step = nativedancer.choices.max_memory_range[1] - nativedancer.choices.max_memory_range[0],
		minimum = nativedancer.choices.max_memory_range[0],
		maximum = nativedancer.choices.max_memory_range[-1]
	)


def listen() -> None:
	MAX_MEMORY_SLIDER.change(update_max_memory, inputs = MAX_MEMORY_SLIDER)


def update_max_memory(max_memory : int) -> None:
	nativedancer.globals.max_memory = max_memory if max_memory > 0 else None
