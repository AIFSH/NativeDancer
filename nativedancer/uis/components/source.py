from typing import Any, IO, Optional
import gradio

import nativedancer.globals
from nativedancer import helperdoc
from nativedancer.utils import is_image
from nativedancer.uis.core import register_ui_component

SOURCE_FILE : Optional[gradio.File] = None
SOURCE_IMAGE : Optional[gradio.Image] = None


def render() -> None:
	global SOURCE_FILE
	global SOURCE_IMAGE

	is_source_image = is_image(nativedancer.globals.source_path)
	SOURCE_FILE = gradio.File(
		file_count = 'single',
		file_types =
		[
			'.png',
			'.jpg',
			'.webp'
		],
		label = helperdoc.get('source_file_label'),
		value = nativedancer.globals.source_path if is_source_image else None
	)
	SOURCE_IMAGE = gradio.Image(
		value = SOURCE_FILE.value['name'] if is_source_image else None,
		visible = is_source_image,
		show_label = False
	)
	register_ui_component('source_image', SOURCE_IMAGE)


def listen() -> None:
	SOURCE_FILE.change(update, inputs = SOURCE_FILE, outputs = SOURCE_IMAGE)


def update(file: IO[Any]) -> gradio.Image:
	if file and is_image(file.name):
		nativedancer.globals.source_path = file.name
		return gradio.Image(value = file.name, visible = True)
	nativedancer.globals.source_path = None
	return gradio.Image(value = None, visible = False)
