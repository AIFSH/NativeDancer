import torch
import numpy as np
from typing import Any, List, Dict, Literal, Optional
from argparse import ArgumentParser
import threading
import cv2
from basicsr.utils.download_util import load_file_from_url
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

import nativedancer.globals
import nativedancer.processors.frame.core as frame_processors
from nativedancer import helperdoc
from nativedancer.content_analyser import clear_content_analyser
from nativedancer.typing import Frame,Update_Process, ProcessMode, ModelValue, OptionsWithModel
from nativedancer.utils import *
from nativedancer.vision import read_image, read_static_image, write_image
from nativedancer.processors.frame import globals as frame_processors_globals
from nativedancer.processors.frame import choices as frame_processors_choices

from nativedancer.third_part.detectron2.config import get_cfg
from nativedancer.third_part.detectron2.engine import DefaultPredictor
from nativedancer.third_part.densepose import add_densepose_config
from nativedancer.third_part.densepose.vis.extractor import DensePoseResultExtractor
from nativedancer.third_part.densepose.vis.densepose_results import DensePoseResultsFineSegmentationVisualizer as Visualizer

FRAME_PROCESSOR = None
THREAD_SEMAPHORE : threading.Semaphore = threading.Semaphore()
THREAD_LOCK : threading.Lock = threading.Lock()
NAME = 'nativedancer.FRAME_PROCESSOR.FRAME_POSE'
MODELS: Dict[str, ModelValue] =\
{
	'DensePose':
	{
		'url': 'https://dl.fbaipublicfiles.com/densepose/densepose_rcnn_R_50_FPN_s1x/165712039/model_final_162be9.pkl',
		'path': resolve_relative_path('../weights/frame_pose'),
		'name': "model_final_162be9.pkl",
		'config': resolve_relative_path("../nativedancer/third_part/densepose/densepose_rcnn_R_50_FPN_s1x.yaml")
	}
}
OPTIONS : Optional[OptionsWithModel] = None


def get_frame_processor() -> Any:
	global FRAME_PROCESSOR

	with THREAD_LOCK:
		if FRAME_PROCESSOR is None:
			model_path = os.path.join(get_options('model').get('path'), get_options('model').get('name'))
			model_config = get_options('model').get('config')
			cfg = get_cfg()
			add_densepose_config(cfg)
			cfg.merge_from_file(model_config)
			cfg.MODEL.WEIGHTS = model_path
			FRAME_PROCESSOR = DefaultPredictor(cfg=cfg)
	return FRAME_PROCESSOR


def clear_frame_processor() -> None:
	global FRAME_PROCESSOR

	FRAME_PROCESSOR = None


def get_options(key : Literal['model']) -> Any:
	global OPTIONS

	if OPTIONS is None:
		OPTIONS =\
		{
			'model': MODELS[frame_processors_globals.frame_pose_model]
		}
	return OPTIONS.get(key)


def set_options(key : Literal['model'], value : Any) -> None:
	global OPTIONS

	OPTIONS[key] = value


def register_args(program : ArgumentParser) -> None:
	program.add_argument('--frame-pose-model', help = helperdoc.get('frame_processor_model_help'), dest = 'frame_pose_model', default = 'DensePose', choices = frame_processors_choices.frame_pose_models)

def apply_args(program : ArgumentParser) -> None:
	args = program.parse_args()
	frame_processors_globals.frame_pose_model = args.frame_pose_model


def pre_check() -> bool:
	if not nativedancer.globals.skip_download:
		download_directory_path = get_options('model').get('path')
		model_url = get_options('model').get('url')
		load_file_from_url(url=model_url, model_dir=download_directory_path, progress=True)
	return True


def pre_process(mode : ProcessMode) -> bool:
	try:
		base_out = os.path.dirname(nativedancer.globals.output_path)
	except:
		base_out = tempfile.gettempdir()
	frame_processors_globals.pose_path = os.path.join(base_out, "pose_out.mp4")
	return True


def post_process() -> None:
	merge_poses()
	clear_frame_processor()
	clear_content_analyser()
	read_static_image.cache_clear()


def merge_poses() -> None:
	# merge video
	fps = nativedancer.globals.fps
	update_status(helperdoc.get('merging_video_fps').format(fps = fps))
	if not merge_video(nativedancer.globals.target_path, fps):
		update_status(helperdoc.get('merging_video_failed'),NAME)
		return
	# handle audio
	if nativedancer.globals.skip_audio:
		update_status(helperdoc.get('skipping_audio'),NAME)
		move_temp(nativedancer.globals.target_path, frame_processors_globals.pose_path)
	else:
		update_status(helperdoc.get('restoring_audio'),NAME)
		if not restore_audio(nativedancer.globals.target_path, frame_processors_globals.pose_path):
			update_status(helperdoc.get('restoring_audio_failed'),NAME)
			move_temp(nativedancer.globals.target_path, frame_processors_globals.pose_path)
	# clear temp
	'''
	update_status(helperdoc.get('clearing_temp'),NAME)
	clear_temp(nativedancer.globals.target_path)
	'''

def densepose_frame(temp_frame:Frame) -> Frame:
	height,width, _ = temp_frame.shape
	predictor = get_frame_processor()
	with torch.no_grad():
		outputs = predictor(temp_frame)['instances']
	results = DensePoseResultExtractor()(outputs)
	cmap = cv2.COLORMAP_VIRIDIS
	# Visualizer outputs black for background, but we want the 0 value of
	# the colormap, so we initialize the array with that value
	arr = cv2.applyColorMap(np.zeros((height, width), dtype=np.uint8), cmap)
	out_frame = Visualizer(alpha=1, cmap=cmap).visualize(arr, results)
	return out_frame

def process_frame(source_face : None, reference_face : None, temp_frame : Frame) -> Frame:
	return densepose_frame(temp_frame)


def process_frames(source_path : str, temp_frame_paths : List[str], update_progress : Update_Process) -> None:
	for temp_frame_path in temp_frame_paths:
		temp_frame = read_image(temp_frame_path)
		result_frame = process_frame(None, None, temp_frame)
		write_image(temp_frame_path, result_frame)
		update_progress()


def process_image(source_path : str, target_path : str, output_path : str) -> None:
	target_frame = read_static_image(target_path)
	result = process_frame(None, None, target_frame)
	write_image(output_path, result)


def process_video(source_path : str, temp_frame_paths : List[str]) -> None:
	frame_processors.multi_process_frames(None, temp_frame_paths, process_frames)
