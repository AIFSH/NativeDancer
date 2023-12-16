from typing import Any, Dict, List, Optional
import cv2
import gradio

import nativedancer.globals
from nativedancer import helperdoc
from nativedancer.core import conditional_set_face_reference
from nativedancer.face_cache import clear_faces_cache
from nativedancer.typing import Frame, Face
from nativedancer.vision import get_video_frame, count_video_frame_total, normalize_frame_color, resize_frame_dimension, read_static_image
from nativedancer.face_analyser import get_one_face, clear_face_analyser
from nativedancer.face_reference import get_face_reference, clear_face_reference
from nativedancer.content_analyser import analyse_frame
from nativedancer.processors.frame.core import load_frame_processor_module
from nativedancer.utils import is_video, is_image
from nativedancer.uis.typing import ComponentName
from nativedancer.uis.core import get_ui_component, register_ui_component

PREVIEW_IMAGE : Optional[gradio.Image] = None
PREVIEW_FRAME_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global PREVIEW_IMAGE
	global PREVIEW_FRAME_SLIDER

	preview_image_args: Dict[str, Any] =\
	{
		'label': helperdoc.get('preview_image_label'),
		'interactive': False
	}
	preview_frame_slider_args: Dict[str, Any] =\
	{
		'label': helperdoc.get('preview_frame_slider_label'),
		'step': 1,
		'minimum': 0,
		'maximum': 100,
		'visible': False
	}
	conditional_set_face_reference()
	source_face = get_one_face(read_static_image(nativedancer.globals.source_path))
	reference_face = get_face_reference() if 'reference' in nativedancer.globals.face_selector_mode else None
	if is_image(nativedancer.globals.target_path):
		target_frame = read_static_image(nativedancer.globals.target_path)
		preview_frame = process_preview_frame(source_face, reference_face, target_frame)
		preview_image_args['value'] = normalize_frame_color(preview_frame)
	if is_video(nativedancer.globals.target_path):
		temp_frame = get_video_frame(nativedancer.globals.target_path, nativedancer.globals.reference_frame_number)
		preview_frame = process_preview_frame(source_face, reference_face, temp_frame)
		preview_image_args['value'] = normalize_frame_color(preview_frame)
		preview_image_args['visible'] = True
		preview_frame_slider_args['value'] = nativedancer.globals.reference_frame_number
		preview_frame_slider_args['maximum'] = count_video_frame_total(nativedancer.globals.target_path)
		preview_frame_slider_args['visible'] = True
	PREVIEW_IMAGE = gradio.Image(**preview_image_args)
	PREVIEW_FRAME_SLIDER = gradio.Slider(**preview_frame_slider_args)
	register_ui_component('preview_frame_slider', PREVIEW_FRAME_SLIDER)


def listen() -> None:
	PREVIEW_FRAME_SLIDER.change(update_preview_image, inputs = PREVIEW_FRAME_SLIDER, outputs = PREVIEW_IMAGE)
	multi_one_component_names : List[ComponentName] =\
	[
		'source_image',
		'target_image',
		'target_video',
		'animate_target_video'
	]
	for component_name in multi_one_component_names:
		component = get_ui_component(component_name)
		if component:
			for method in [ 'upload', 'change', 'clear' ]:
				getattr(component, method)(update_preview_image, inputs = PREVIEW_FRAME_SLIDER, outputs = PREVIEW_IMAGE)
	multi_two_component_names : List[ComponentName] =\
	[
		'target_image',
		'target_video',
		'animate_target_video'
	]
	for component_name in multi_two_component_names:
		component = get_ui_component(component_name)
		if component:
			for method in [ 'upload', 'change', 'clear' ]:
				getattr(component, method)(update_preview_frame_slider, outputs = PREVIEW_FRAME_SLIDER)
	select_component_names : List[ComponentName] =\
	[
		'reference_face_position_gallery',
		'face_analyser_order_dropdown',
		'face_analyser_age_dropdown',
		'face_analyser_gender_dropdown'
	]
	for component_name in select_component_names:
		component = get_ui_component(component_name)
		if component:
			component.select(update_preview_image, inputs = PREVIEW_FRAME_SLIDER, outputs = PREVIEW_IMAGE)
	change_one_component_names : List[ComponentName] =\
	[
		'frame_processors_checkbox_group',
		'face_debugger_items_checkbox_group',
		'face_enhancer_model_dropdown',
		'face_enhancer_blend_slider',
		'frame_enhancer_model_dropdown',
		'frame_enhancer_blend_slider',
		'face_selector_mode_dropdown',
		'reference_face_distance_slider',
		'face_mask_blur_slider',
		'face_mask_padding_top_slider',
		'face_mask_padding_bottom_slider',
		'face_mask_padding_left_slider',
		'face_mask_padding_right_slider'
	]
	for component_name in change_one_component_names:
		component = get_ui_component(component_name)
		if component:
			component.change(update_preview_image, inputs = PREVIEW_FRAME_SLIDER, outputs = PREVIEW_IMAGE)
	change_two_component_names : List[ComponentName] =\
	[
		'face_swapper_model_dropdown',
		'face_detector_model_dropdown',
		'face_detector_size_dropdown',
		'face_detector_score_slider'
	]
	for component_name in change_two_component_names:
		component = get_ui_component(component_name)
		if component:
			component.change(clear_and_update_preview_image, inputs = PREVIEW_FRAME_SLIDER, outputs = PREVIEW_IMAGE)


def clear_and_update_preview_image(frame_number : int = 0) -> gradio.Image:
	clear_face_analyser()
	clear_face_reference()
	clear_faces_cache()
	return update_preview_image(frame_number)


def update_preview_image(frame_number : int = 0) -> gradio.Image:
	conditional_set_face_reference()
	source_face = get_one_face(read_static_image(nativedancer.globals.source_path))
	reference_face = get_face_reference() if 'reference' in nativedancer.globals.face_selector_mode else None
	if is_image(nativedancer.globals.target_path):
		target_frame = read_static_image(nativedancer.globals.target_path)
		preview_frame = process_preview_frame(source_face, reference_face, target_frame)
		preview_frame = normalize_frame_color(preview_frame)
		return gradio.Image(value = preview_frame)
	if is_video(nativedancer.globals.target_path):
		temp_frame = get_video_frame(nativedancer.globals.target_path, frame_number)
		preview_frame = process_preview_frame(source_face, reference_face, temp_frame)
		preview_frame = normalize_frame_color(preview_frame)
		return gradio.Image(value = preview_frame)
	return gradio.Image(value = None)


def update_preview_frame_slider() -> gradio.Slider:
	if is_video(nativedancer.globals.target_path):
		video_frame_total = count_video_frame_total(nativedancer.globals.target_path)
		return gradio.Slider(maximum = video_frame_total, visible = True)
	return gradio.Slider(value = None, maximum = None, visible = False)


def process_preview_frame(source_face : Face, reference_face : Face, temp_frame : Frame) -> Frame:
	temp_frame = resize_frame_dimension(temp_frame, 640, 640)
	if analyse_frame(temp_frame):
		return cv2.GaussianBlur(temp_frame, (99, 99), 0)
	for frame_processor in nativedancer.globals.frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
		if frame_processor_module.pre_process('preview'):
			temp_frame = frame_processor_module.process_frame(
				source_face,
				reference_face,
				temp_frame
			)
	return temp_frame
