from typing import Optional
import gradio

import nativedancer.globals
import nativedancer.choices
from nativedancer import helperdoc

EXECUTION_THREAD_COUNT_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global EXECUTION_THREAD_COUNT_SLIDER

	EXECUTION_THREAD_COUNT_SLIDER = gradio.Slider(
		label = helperdoc.get('execution_thread_count_slider_label'),
		value = nativedancer.globals.execution_thread_count,
		step = nativedancer.choices.execution_thread_count_range[1] - nativedancer.choices.execution_thread_count_range[0],
		minimum = nativedancer.choices.execution_thread_count_range[0],
		maximum = nativedancer.choices.execution_thread_count_range[-1]
	)


def listen() -> None:
	EXECUTION_THREAD_COUNT_SLIDER.change(update_execution_thread_count, inputs = EXECUTION_THREAD_COUNT_SLIDER)


def update_execution_thread_count(execution_thread_count : int = 1) -> None:
	nativedancer.globals.execution_thread_count = execution_thread_count

