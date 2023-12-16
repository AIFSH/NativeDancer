import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
import gradio
from PIL import Image
import torch
import numpy as np
from typing import Any, List, Dict, Literal, Optional
from argparse import ArgumentParser
import threading
import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from huggingface_hub import snapshot_download
from nativedancer.vision import get_video_frame
from nativedancer.core import conditional_set_face_reference
import nativedancer.globals
import nativedancer.processors.frame.core as frame_processors
from nativedancer import helperdoc
from nativedancer.content_analyser import clear_content_analyser
from nativedancer.typing import Frame,Update_Process, ProcessMode, ModelValue, OptionsWithModel
from nativedancer.utils import *
from nativedancer.vision import read_image, read_static_image, write_image
from nativedancer.processors.frame import globals as frame_processors_globals
from nativedancer.processors.frame import choices as frame_processors_choices
from nativedancer.third_part.magicanimate.animate import MagicAnimate


FRAME_PROCESSOR = None
THREAD_SEMAPHORE : threading.Semaphore = threading.Semaphore()
THREAD_LOCK : threading.Lock = threading.Lock()
NAME = 'nativedancer.FRAME_PROCESSOR.POSE_FRAME'
MODELS: Dict[str, ModelValue] =\
{
	'MagicAnimate':
	{
		'url': 'https://hf-mirror.com/zcxu-eric/MagicAnimate/tree/main',
		'path': resolve_relative_path('../weights/pose_frame'),
		"repo_id": "zcxu-eric/MagicAnimate"
	}
}
OPTIONS : Optional[OptionsWithModel] = None


def get_frame_processor() -> Any:
	global FRAME_PROCESSOR

	with THREAD_LOCK:
		if FRAME_PROCESSOR is None:
			model_path = get_options('model').get('path')
			FRAME_PROCESSOR = MagicAnimate()
	return FRAME_PROCESSOR


def clear_frame_processor() -> None:
	global FRAME_PROCESSOR

	FRAME_PROCESSOR = None


def get_options(key : Literal['model']) -> Any:
	global OPTIONS

	if OPTIONS is None:
		OPTIONS =\
		{
			'model': MODELS[frame_processors_globals.pose_frame_model]
		}
	return OPTIONS.get(key)


def set_options(key : Literal['model'], value : Any) -> None:
	global OPTIONS

	OPTIONS[key] = value


def register_args(program : ArgumentParser) -> None:
	program.add_argument('--pose-frame-model', help = helperdoc.get('frame_processor_model_help'), dest = 'pose_frame_model', default = 'MagicAnimate', choices = frame_processors_choices.pose_frame_models)
	program.add_argument('--random-seed', help = helperdoc.get('random_seed_help'), dest = 'random_seed', default = -1, type=int)
	program.add_argument('--guidance-scale', help = helperdoc.get('guidance_scale_help'), dest = 'guidance_scale', default = 7.5, type=float)
	program.add_argument('--step', help = helperdoc.get('step_help'), dest = 'step', default = 25, type=int)

def apply_args(program : ArgumentParser) -> None:
	args = program.parse_args()
	frame_processors_globals.pose_frame_model = args.pose_frame_model
	frame_processors_globals.random_seed = args.random_seed
	frame_processors_globals.guidance_scale = args.guidance_scale
	frame_processors_globals.step = args.step


def pre_check() -> bool:
	if not nativedancer.globals.skip_download:
		repo_id = get_options('model').get('repo_id')
		model_path = get_options('model').get('path')
		magic_path = os.path.join(model_path, 'MagicAnimate')
		snapshot_download(repo_id=repo_id, cache_dir=model_path,local_dir=magic_path,local_dir_use_symlinks=True)
		# download sd model
		# subprocess.call(["sh","sd1-5.sh"], shell=True)
	    
		sd_path = os.path.join(model_path, 'stable-diffusion-v1-5')
		# pure diffuser sd model
		snapshot_download(repo_id="bdsqlsz/stable-diffusion-v1-5",cache_dir=model_path,local_dir=sd_path,local_dir_use_symlinks=True)
		
		sd_vae_path = os.path.join(model_path, 'sd-vae-ft-mse')
		snapshot_download(repo_id="stabilityai/sd-vae-ft-mse", cache_dir=model_path,local_dir=sd_vae_path,local_dir_use_symlinks=True)
	return True


def pre_process(mode : ProcessMode) -> bool:
	try:
		base_out = os.path.dirname(nativedancer.globals.output_path)
	except:
		base_out = tempfile.gettempdir()
	frame_processors_globals.animate_path = os.path.join(base_out,'animate_out.mp4')
	return True


def post_process() -> None:
	nativedancer.globals.cached_path = nativedancer.globals.target_path
	# update target_path
	nativedancer.globals.target_path = frame_processors_globals.animate_path
	if nativedancer.globals.headless:
		conditional_set_face_reference()
	# clear temp
	update_status(helperdoc.get('clearing_temp'),NAME)
	clear_temp(frame_processors_globals.animate_path)
	clear_frame_processor()
	clear_content_analyser()
	read_static_image.cache_clear()

def extract_animate_frames(path:str) -> None:
	# create temp
	fps = detect_fps(path)
	update_status(helperdoc.get('creating_temp'), NAME)
	create_temp(path)
	# extract frames
	update_status(helperdoc.get('extracting_frames_fps').format(fps = fps))
	return extract_frames(path, fps=fps)


def process_frame(source_face : None, reference_face : None, temp_frame : Frame) -> Frame:
	if nativedancer.globals.cached_path:
		temp_path = get_temp_frame_paths(nativedancer.globals.cached_path)
		frame = read_image(temp_path[0])
		if frame is not None:
			return frame
	return temp_frame

def process_frames(source_path : str, temp_frame_paths : List[str],update_progress : Update_Process) -> None:
	temp_animate_frame_paths = get_temp_frame_paths(frame_processors_globals.animate_path)
	for temp_frame_path,temp_animate_frame_path in zip(temp_frame_paths,temp_animate_frame_paths):
		temp_frame = read_image(temp_animate_frame_path)
		result_frame = process_frame(None, None, temp_frame)
		write_image(temp_frame_path, result_frame)
		update_progress()


def process_image(source_path : str, target_path : str, output_path : str) -> None:
	target_frame = read_static_image(target_path)
	result = process_frame(None, None, target_frame)
	write_image(output_path, result)

def read_animate_image(image, size=512):
    img_arry = Image.open(image).resize((size,size))
    return np.array(img_arry)

def process_video(source_path : str, temp_frame_paths : List[str]) -> None:
	magic_animate = get_frame_processor()
	source_image = read_animate_image(source_path)
	magic_animate(source_image=source_image, 
				motion_sequence=frame_processors_globals.pose_path, 
				output_file=frame_processors_globals.animate_path, 
				fps = nativedancer.globals.fps,
				random_seed=frame_processors_globals.random_seed, 
				step=frame_processors_globals.step, 
				guidance_scale=frame_processors_globals.guidance_scale, 
				size=512)
	
	if extract_animate_frames(frame_processors_globals.animate_path):
		temp_animate_frame_paths = get_temp_frame_paths(frame_processors_globals.animate_path)
		for temp_frame_path,temp_animate_frame_path in tqdm(zip(temp_frame_paths,temp_animate_frame_paths),
													   desc="Write image back to temp path", total=len(temp_animate_frame_paths)):
			temp_frame = read_image(temp_animate_frame_path)
			write_image(temp_frame_path, temp_frame)
	