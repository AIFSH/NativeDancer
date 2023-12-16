from typing import Tuple, Optional
import gradio

import nativedancer.globals
from nativedancer import helperdoc
from nativedancer.core import limit_resources, process_facefusion_video
from nativedancer.uis.core import get_ui_component
from nativedancer.utils import is_image, is_video, normalize_output_path, clear_temp

OUTPUT_IMAGE : Optional[gradio.Image] = None
OUTPUT_VIDEO : Optional[gradio.Video] = None
OUTPUT_START_BUTTON : Optional[gradio.Button] = None
OUTPUT_CLEAR_BUTTON : Optional[gradio.Button] = None


def render() -> None:
	global OUTPUT_IMAGE
	global OUTPUT_VIDEO
	global OUTPUT_START_BUTTON
	global OUTPUT_CLEAR_BUTTON

	OUTPUT_IMAGE = gradio.Image(
		label = helperdoc.get('output_image_or_video_label'),
		visible = False
	)
	OUTPUT_VIDEO = gradio.Video(
		label = helperdoc.get('output_image_or_video_label')
	)
	OUTPUT_START_BUTTON = gradio.Button(
		value = helperdoc.get('start_button_label'),
		variant = 'primary',
		size = 'sm'
	)
	OUTPUT_CLEAR_BUTTON = gradio.Button(
		value = helperdoc.get('clear_button_label'),
		size = 'sm'
	)


def listen() -> None:
	output_path_textbox = get_ui_component('output_path_textbox')
	if output_path_textbox:
		OUTPUT_START_BUTTON.click(start, inputs = output_path_textbox, outputs = [ OUTPUT_IMAGE, OUTPUT_VIDEO ])
	OUTPUT_CLEAR_BUTTON.click(clear, outputs = [ OUTPUT_IMAGE, OUTPUT_VIDEO ])


def start(output_path : str) -> Tuple[gradio.Image, gradio.Video]:
	nativedancer.globals.output_path = normalize_output_path(nativedancer.globals.source_path, nativedancer.globals.target_path, output_path)
	limit_resources()
	# conditional_process()
	process_facefusion_video()
	if is_image(nativedancer.globals.output_path):
		return gradio.Image(value = nativedancer.globals.output_path, visible = True), gradio.Video(value = None, visible = False)
	if is_video(nativedancer.globals.output_path):
		return gradio.Image(value = None, visible = False), gradio.Video(value = nativedancer.globals.output_path, visible = True)
	return gradio.Image(), gradio.Video()


def clear() -> Tuple[gradio.Image, gradio.Video]:
	if nativedancer.globals.target_path:
		clear_temp(nativedancer.globals.target_path)
	return gradio.Image(value = None), gradio.Video(value = None)
