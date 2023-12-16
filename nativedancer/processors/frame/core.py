import sys
import importlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from types import ModuleType
from typing import Any, List
from tqdm import tqdm

import nativedancer.globals
from nativedancer.typing import Process_Frames
from nativedancer import helperdoc
from nativedancer.utils import encode_execution_providers,update_status

FRAME_PROCESSORS_MODULES : List[ModuleType] = []
FRAME_PROCESSORS_METHODS =\
[
	'get_frame_processor',
	'clear_frame_processor',
	'get_options',
	'set_options',
	'register_args',
	'apply_args',
	'pre_check',
	'pre_process',
	'process_frame',
	'process_frames',
	'process_image',
	'process_video',
	'post_process'
]


def load_frame_processor_module(frame_processor : str) -> Any:
	try:
		frame_processor_module = importlib.import_module('nativedancer.processors.frame.modules.' + frame_processor)
		for method_name in FRAME_PROCESSORS_METHODS:
			if not hasattr(frame_processor_module, method_name):
				raise NotImplementedError
	except ModuleNotFoundError:
		raise ModuleNotFoundError
		sys.exit(helperdoc.get('frame_processor_not_loaded').format(frame_processor = frame_processor))
	except NotImplementedError:
		sys.exit(helperdoc.get('frame_processor_not_implemented').format(frame_processor = frame_processor))
	return frame_processor_module


def get_frame_processors_modules(frame_processors : List[str]) -> List[ModuleType]:
	global FRAME_PROCESSORS_MODULES

	if not FRAME_PROCESSORS_MODULES:
		for frame_processor in frame_processors:
			frame_processor_module = load_frame_processor_module(frame_processor)
			FRAME_PROCESSORS_MODULES.append(frame_processor_module)
	return FRAME_PROCESSORS_MODULES


def clear_frame_processors_modules() -> None:
	global FRAME_PROCESSORS_MODULES

	for frame_processor_module in get_frame_processors_modules(nativedancer.globals.frame_processors):
		frame_processor_module.clear_frame_processor()
	FRAME_PROCESSORS_MODULES = []


def multi_process_frames(source_path : str, temp_frame_paths : List[str], process_frames : Process_Frames) -> None:
	with tqdm(total = len(temp_frame_paths), desc = helperdoc.get('processing'), unit = 'frame', ascii = ' =') as progress:
		progress.set_postfix(
		{
			'execution_providers': encode_execution_providers(nativedancer.globals.execution_providers),
			'execution_thread_count': nativedancer.globals.execution_thread_count,
			'execution_queue_count': nativedancer.globals.execution_queue_count
		})
		with ThreadPoolExecutor(max_workers = nativedancer.globals.execution_thread_count) as executor:
			futures = []
			queue_temp_frame_paths : Queue[str] = create_queue(temp_frame_paths)
			queue_per_future = max(len(temp_frame_paths) // nativedancer.globals.execution_thread_count * nativedancer.globals.execution_queue_count, 1)
			while not queue_temp_frame_paths.empty():
				payload_temp_frame_paths = pick_queue(queue_temp_frame_paths, queue_per_future)
				future = executor.submit(process_frames, source_path, payload_temp_frame_paths, progress.update)
				futures.append(future)
			for future_done in as_completed(futures):
				future_done.result()


def create_queue(temp_frame_paths : List[str]) -> Queue[str]:
	queue : Queue[str] = Queue()
	for frame_path in temp_frame_paths:
		queue.put(frame_path)
	return queue


def pick_queue(queue : Queue[str], queue_per_future : int) -> List[str]:
	queues = []
	for _ in range(queue_per_future):
		if not queue.empty():
			queues.append(queue.get())
	return queues
