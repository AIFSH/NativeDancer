from typing import Optional, Tuple, List
import tempfile
import gradio,torch

import nativedancer.globals
import nativedancer.choices
from nativedancer import helperdoc
from nativedancer.typing import OutputVideoEncoder
from nativedancer.utils import is_image, is_video
from nativedancer.uis.typing import ComponentName
import nativedancer.processors.frame.globals as frame_processors_globals
from nativedancer.uis.core import get_ui_component, register_ui_component
from nativedancer.core import process_animate_video
from nativedancer.processors.frame.core import get_frame_processors_modules

ANIMATE_VIDEO : Optional[gradio.Video] = None
ANIMATE_START_BUTTON : Optional[gradio.Button] = None
ANIMATE_SEED_TEXTBOX : Optional[gradio.Textbox] = None
ANIMATE_STEP_TEXTBOX : Optional[gradio.Textbox] = None
ANIMATE_SCALE_TEXTBOX : Optional[gradio.Textbox] = None

def render() -> None:
	global ANIMATE_VIDEO
	global ANIMATE_SEED_TEXTBOX
	global ANIMATE_STEP_TEXTBOX
	global ANIMATE_SCALE_TEXTBOX
	global ANIMATE_START_BUTTON
	ANIMATE_STEP_TEXTBOX = gradio.Textbox(
		label = helperdoc.get('animate_step_label'),
		value = frame_processors_globals.step or 25,
		max_lines = 1
	)
	ANIMATE_SCALE_TEXTBOX = gradio.Textbox(
		label = helperdoc.get('animate_scale_label'),
		value = frame_processors_globals.guidance_scale or 7.5,
		max_lines = 1
	)
	ANIMATE_SEED_TEXTBOX = gradio.Textbox(
		label = helperdoc.get('animate_seed_label'),
		value = frame_processors_globals.random_seed or torch.seed(),
		max_lines = 1
	)
	ANIMATE_VIDEO = gradio.Video(
		label = helperdoc.get('animate_video_label')
	)
	ANIMATE_START_BUTTON = gradio.Button(
		value = helperdoc.get('animate_start_label'),
		variant = 'primary',
		size = 'sm'
	)
	register_ui_component('animate_target_video', ANIMATE_VIDEO)


def listen() -> None:
	ANIMATE_SEED_TEXTBOX.change(update_animate_seed, inputs = ANIMATE_SEED_TEXTBOX)
	ANIMATE_STEP_TEXTBOX.change(update_animate_step, inputs = ANIMATE_STEP_TEXTBOX)
	ANIMATE_SCALE_TEXTBOX.change(update_animate_scale, inputs = ANIMATE_SCALE_TEXTBOX)
	ANIMATE_START_BUTTON.click(start, outputs= ANIMATE_VIDEO)

def start():
	process_animate_video()
	if is_video(frame_processors_globals.animate_path):
		return gradio.Video(value=frame_processors_globals.animate_path, visible=True)
	return gradio.Video()

def update_animate_seed(seed : str) -> None:
	frame_processors_globals.random_seed = int(seed)

def update_animate_step(step : str) -> None:
	frame_processors_globals.step = int(step)

def update_animate_scale(scale : str) -> None:
	frame_processors_globals.step = float(scale)