from typing import List, Optional
import gradio

import nativedancer.globals
from nativedancer import helperdoc
from nativedancer.processors.frame.core import load_frame_processor_module, clear_frame_processors_modules
from nativedancer.utils import list_module_names
from nativedancer.uis.core import register_ui_component

FRAME_PROCESSORS_CHECKBOX_GROUP : Optional[gradio.CheckboxGroup] = None


def render() -> None:
	global FRAME_PROCESSORS_CHECKBOX_GROUP

	FRAME_PROCESSORS_CHECKBOX_GROUP = gradio.CheckboxGroup(
		label = helperdoc.get('frame_processors_checkbox_group_label'),
		choices = sort_frame_processors(nativedancer.globals.frame_processors),
		value = nativedancer.globals.frame_processors
	)
	register_ui_component('frame_processors_checkbox_group', FRAME_PROCESSORS_CHECKBOX_GROUP)


def listen() -> None:
	FRAME_PROCESSORS_CHECKBOX_GROUP.change(update_frame_processors, inputs = FRAME_PROCESSORS_CHECKBOX_GROUP, outputs = FRAME_PROCESSORS_CHECKBOX_GROUP)


def update_frame_processors(frame_processors : List[str]) -> gradio.CheckboxGroup:
	tmp_list:List[str] = [ 'frame_pose', 'pose_frame'] 
	for f in frame_processors:
		if f not in tmp_list:
			tmp_list.append(f)
	nativedancer.globals.frame_processors = tmp_list
	frame_processors = tmp_list
	clear_frame_processors_modules()
	for frame_processor in frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
		if not frame_processor_module.pre_check():
			return gradio.CheckboxGroup()
	return gradio.CheckboxGroup(value = frame_processors, choices = sort_frame_processors(frame_processors))


def sort_frame_processors(frame_processors : List[str]) -> list[str]:
	available_frame_processors = list_module_names('nativedancer/processors/frame/modules')
	return sorted(available_frame_processors, key = lambda frame_processor : frame_processors.index(frame_processor) if frame_processor in frame_processors else len(frame_processors))
