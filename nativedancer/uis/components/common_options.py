from typing import Optional, List
import gradio

import nativedancer.globals
from nativedancer import helperdoc
from nativedancer.uis import choices as uis_choices

COMMON_OPTIONS_CHECKBOX_GROUP : Optional[gradio.Checkboxgroup] = None


def render() -> None:
	global COMMON_OPTIONS_CHECKBOX_GROUP

	value = []
	if nativedancer.globals.keep_fps:
		value.append('keep-fps')
	if nativedancer.globals.keep_temp:
		value.append('keep-temp')
	if nativedancer.globals.skip_audio:
		value.append('skip-audio')
	if nativedancer.globals.skip_download:
		value.append('skip-download')
	COMMON_OPTIONS_CHECKBOX_GROUP = gradio.Checkboxgroup(
		label = helperdoc.get('common_options_checkbox_group_label'),
		choices = uis_choices.common_options,
		value = value
	)


def listen() -> None:
	COMMON_OPTIONS_CHECKBOX_GROUP.change(update, inputs = COMMON_OPTIONS_CHECKBOX_GROUP)


def update(common_options : List[str]) -> None:
	nativedancer.globals.keep_fps = 'keep-fps' in common_options
	nativedancer.globals.keep_temp = 'keep-temp' in common_options
	nativedancer.globals.skip_audio = 'skip-audio' in common_options
	nativedancer.globals.skip_download = 'skip-download' in common_options
