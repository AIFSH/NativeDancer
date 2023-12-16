from typing import Optional
import gradio

import nativedancer.globals
import nativedancer.choices
from nativedancer import helperdoc

EXECUTION_QUEUE_COUNT_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global EXECUTION_QUEUE_COUNT_SLIDER

	EXECUTION_QUEUE_COUNT_SLIDER = gradio.Slider(
		label = helperdoc.get('execution_queue_count_slider_label'),
		value = nativedancer.globals.execution_queue_count,
		step = nativedancer.choices.execution_queue_count_range[1] - nativedancer.choices.execution_queue_count_range[0],
		minimum = nativedancer.choices.execution_queue_count_range[0],
		maximum = nativedancer.choices.execution_queue_count_range[-1]
	)


def listen() -> None:
	EXECUTION_QUEUE_COUNT_SLIDER.change(update_execution_queue_count, inputs = EXECUTION_QUEUE_COUNT_SLIDER)


def update_execution_queue_count(execution_queue_count : int = 1) -> None:
	nativedancer.globals.execution_queue_count = execution_queue_count
