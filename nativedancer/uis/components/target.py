from typing import Any, IO, Tuple, Optional
import gradio

import nativedancer.globals
from nativedancer import helperdoc
from nativedancer.face_cache import clear_faces_cache
from nativedancer.face_reference import clear_face_reference
from nativedancer.utils import is_image, is_video
from nativedancer.uis.core import register_ui_component

TARGET_FILE : Optional[gradio.File] = None
TARGET_IMAGE : Optional[gradio.Image] = None
TARGET_VIDEO : Optional[gradio.Video] = None


def render() -> None:
	global TARGET_FILE
	global TARGET_IMAGE
	global TARGET_VIDEO

	is_target_image = is_image(nativedancer.globals.target_path)
	is_target_video = is_video(nativedancer.globals.target_path)
	TARGET_FILE = gradio.File(
		label = helperdoc.get('target_file_label'),
		file_count = 'single',
		file_types =
		[
			'.png',
			'.jpg',
			'.webp',
			'.mp4'
		],
		value = nativedancer.globals.target_path if is_target_image or is_target_video else None
	)
	TARGET_IMAGE = gradio.Image(
		value = TARGET_FILE.value['name'] if is_target_image else None,
		visible = is_target_image,
		show_label = False
	)
	TARGET_VIDEO = gradio.Video(
		value = TARGET_FILE.value['name'] if is_target_video else None,
		visible = is_target_video,
		show_label = False
	)
	register_ui_component('target_image', TARGET_IMAGE)
	register_ui_component('target_video', TARGET_VIDEO)


def listen() -> None:
	TARGET_FILE.change(update, inputs = TARGET_FILE, outputs = [ TARGET_IMAGE, TARGET_VIDEO ])


def update(file : IO[Any]) -> Tuple[gradio.Image, gradio.Video]:
	clear_face_reference()
	clear_faces_cache()
	if file and is_image(file.name):
		nativedancer.globals.target_path = file.name
		return gradio.Image(value = file.name, visible = True), gradio.Video(value = None, visible = False)
	if file and is_video(file.name):
		nativedancer.globals.target_path = file.name
		return gradio.Image(value = None, visible = False), gradio.Video(value = file.name, visible = True)
	nativedancer.globals.target_path = None
	return gradio.Image(value = None, visible = False), gradio.Video(value = None, visible = False)
