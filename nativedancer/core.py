import signal,sys
import warnings
import onnxruntime
import nativedancer.globals
import nativedancer.choices
from nativedancer.utils import *
from nativedancer import helperdoc,content_analyser,face_analyser
from argparse import ArgumentParser,HelpFormatter
from nativedancer.content_analyser import analyse_image, analyse_video
from nativedancer.processors.frame.core import load_frame_processor_module,get_frame_processors_modules
from nativedancer.face_analyser import get_one_face
from nativedancer.face_reference import get_face_reference, set_face_reference
from nativedancer.vision import get_video_frame, read_image
onnxruntime.set_default_logger_severity(3)
warnings.filterwarnings('ignore', category = UserWarning, module = 'gradio')
warnings.filterwarnings('ignore', category = UserWarning, module = 'torchvision')

def cli() -> None:
    signal.signal(signal.SIGINT, lambda signal_number, frame: destroy())
    program = ArgumentParser(formatter_class = lambda prog: HelpFormatter(prog, max_help_position = 120), add_help = False)
    # general
    program.add_argument('-s', '--source', help = helperdoc.get('source_help'), dest = 'source_path')
    program.add_argument('-t', '--target', help = helperdoc.get('target_help'), dest = 'target_path')
    program.add_argument('-o', '--output', help = helperdoc.get('output_help'), dest = 'output_path')
	
    # misc
    group_misc = program.add_argument_group('misc')
    group_misc.add_argument('--skip-download', help = helperdoc.get('skip_download_help'), dest = 'skip_download', action = 'store_true')
    group_misc.add_argument('--headless', help = helperdoc.get('headless_help'), dest = 'headless', action = 'store_true')

    # execution
    group_execution = program.add_argument_group('execution')
    group_execution.add_argument('--execution-providers', help = helperdoc.get('execution_providers_help'), dest = 'execution_providers', default = [ 'cuda' ], choices = encode_execution_providers(onnxruntime.get_available_providers()), nargs = '+')
    group_execution.add_argument('--execution-thread-count', help = helperdoc.get('execution_thread_count_help'), dest = 'execution_thread_count', type = int, default = 4, choices = nativedancer.choices.execution_thread_count_range, metavar = create_metavar(nativedancer.choices.execution_thread_count_range))
    group_execution.add_argument('--execution-queue-count', help = helperdoc.get('execution_queue_count_help'), dest = 'execution_queue_count', type = int, default = 1, choices = nativedancer.choices.execution_queue_count_range, metavar = create_metavar(nativedancer.choices.execution_queue_count_range))
    group_execution.add_argument('--max-memory', help = helperdoc.get('max_memory_help'), dest = 'max_memory', type = int, choices = nativedancer.choices.max_memory_range, metavar = create_metavar(nativedancer.choices.max_memory_range))
    
	# face analyser
    group_face_analyser = program.add_argument_group('face analyser')
    group_face_analyser.add_argument('--face-analyser-order', help = helperdoc.get('face_analyser_order_help'), dest = 'face_analyser_order', default = 'left-right', choices = nativedancer.choices.face_analyser_orders)
    group_face_analyser.add_argument('--face-analyser-age', help = helperdoc.get('face_analyser_age_help'), dest = 'face_analyser_age', choices = nativedancer.choices.face_analyser_ages)
    group_face_analyser.add_argument('--face-analyser-gender', help = helperdoc.get('face_analyser_gender_help'), dest = 'face_analyser_gender', choices = nativedancer.choices.face_analyser_genders)
    group_face_analyser.add_argument('--face-detector-model', help = helperdoc.get('face_detector_model_help'), dest = 'face_detector_model', default = 'retinaface', choices = nativedancer.choices.face_detector_models)
    group_face_analyser.add_argument('--face-detector-size', help = helperdoc.get('face_detector_size_help'), dest = 'face_detector_size', default = '640x640', choices = nativedancer.choices.face_detector_sizes)
    group_face_analyser.add_argument('--face-detector-score', help = helperdoc.get('face_detector_score_help'), dest = 'face_detector_score', type = float, default = 0.5, choices = nativedancer.choices.face_detector_score_range, metavar = create_metavar(nativedancer.choices.face_detector_score_range))
	# face selector
    group_face_selector = program.add_argument_group('face selector')
    group_face_selector.add_argument('--face-selector-mode', help = helperdoc.get('face_selector_mode_help'), dest = 'face_selector_mode', default = 'reference', choices = nativedancer.choices.face_selector_modes)
    group_face_selector.add_argument('--reference-face-position', help = helperdoc.get('reference_face_position_help'), dest = 'reference_face_position', type = int, default = 0)
    group_face_selector.add_argument('--reference-face-distance', help = helperdoc.get('reference_face_distance_help'), dest = 'reference_face_distance', type = float, default = 0.6, choices = nativedancer.choices.reference_face_distance_range, metavar = create_metavar(nativedancer.choices.reference_face_distance_range))
    group_face_selector.add_argument('--reference-frame-number', help = helperdoc.get('reference_frame_number_help'), dest = 'reference_frame_number', type = int, default = 0)
	# face mask
    group_face_mask = program.add_argument_group('face mask')
    group_face_mask.add_argument('--face-mask-blur', help = helperdoc.get('face_mask_blur_help'), dest = 'face_mask_blur', type = float, default = 0.3, choices = nativedancer.choices.face_mask_blur_range, metavar = create_metavar(nativedancer.choices.face_mask_blur_range))
    group_face_mask.add_argument('--face-mask-padding', help = helperdoc.get('face_mask_padding_help'), dest = 'face_mask_padding', type = int, default = [ 0, 0, 0, 0 ], nargs = '+')

    # frame extraction
    group_frame_extraction = program.add_argument_group('frame extraction')
    group_frame_extraction.add_argument('--trim-frame-start', help = helperdoc.get('trim_frame_start_help'), dest = 'trim_frame_start', type = int)
    group_frame_extraction.add_argument('--trim-frame-end', help = helperdoc.get('trim_frame_end_help'), dest = 'trim_frame_end', type = int)
    group_frame_extraction.add_argument('--temp-frame-format', help = helperdoc.get('temp_frame_format_help'), dest = 'temp_frame_format', default = 'jpg', choices = nativedancer.choices.temp_frame_formats)
    group_frame_extraction.add_argument('--temp-frame-quality', help = helperdoc.get('temp_frame_quality_help'), dest = 'temp_frame_quality', type = int, default = 100, choices = nativedancer.choices.temp_frame_quality_range, metavar = create_metavar(nativedancer.choices.temp_frame_quality_range))
    group_frame_extraction.add_argument('--keep-temp', help = helperdoc.get('keep_temp_help'), dest = 'keep_temp', action = 'store_true')
    # output creation
    group_output_creation = program.add_argument_group('output creation')
    group_output_creation.add_argument('--output-image-quality', help = helperdoc.get('output_image_quality_help'), dest = 'output_image_quality', type = int, default = 80, choices = nativedancer.choices.output_image_quality_range, metavar = create_metavar(nativedancer.choices.output_image_quality_range))
    group_output_creation.add_argument('--output-video-encoder', help = helperdoc.get('output_video_encoder_help'), dest = 'output_video_encoder', default = 'libx264', choices = nativedancer.choices.output_video_encoders)
    group_output_creation.add_argument('--output-video-quality', help = helperdoc.get('output_video_quality_help'), dest = 'output_video_quality', type = int, default = 80, choices = nativedancer.choices.output_video_quality_range, metavar = create_metavar(nativedancer.choices.output_video_quality_range))
    group_output_creation.add_argument('--keep-fps', help = helperdoc.get('keep_fps_help'), dest = 'keep_fps', action = 'store_true')
    group_output_creation.add_argument('--skip-audio', help = helperdoc.get('skip_audio_help'), dest = 'skip_audio', action = 'store_true')

    # frame processors
    available_frame_processors = list_module_names('nativedancer/processors/frame/modules')
    program = ArgumentParser(parents = [ program ], formatter_class = program.formatter_class, add_help = True)
    group_frame_processors = program.add_argument_group('frame processors')
    group_frame_processors.add_argument('--frame-processors', help = helperdoc.get('frame_processors_help').format(choices = ', '.join(available_frame_processors)), dest = 'frame_processors', default = [ 'frame_pose', 'pose_frame', 'face_swapper', 'face_enhancer','frame_enhancer'], nargs = '+')
    for frame_processor in available_frame_processors:
        frame_processor_module = load_frame_processor_module(frame_processor)
        frame_processor_module.register_args(group_frame_processors)
    # uis
    group_uis = program.add_argument_group('uis')
    group_uis.add_argument('--ui-layouts', help = helperdoc.get('ui_layouts_help').format(choices = ', '.join(list_module_names('nativedancer/uis/layouts'))), dest = 'ui_layouts', default = [ 'default' ], nargs = '+')
    run(program)

def apply_args(program : ArgumentParser) -> None:
	args = program.parse_args()
	# general
	nativedancer.globals.source_path = args.source_path
	nativedancer.globals.target_path = args.target_path
	nativedancer.globals.output_path = normalize_output_path(nativedancer.globals.source_path, nativedancer.globals.target_path, args.output_path)
	# misc
	nativedancer.globals.skip_download = args.skip_download
	nativedancer.globals.headless = args.headless
	# execution
	nativedancer.globals.execution_providers = decode_execution_providers(args.execution_providers)
	nativedancer.globals.execution_thread_count = args.execution_thread_count
	nativedancer.globals.execution_queue_count = args.execution_queue_count
	nativedancer.globals.max_memory = args.max_memory
	# frame extraction
	nativedancer.globals.trim_frame_start = args.trim_frame_start
	nativedancer.globals.trim_frame_end = args.trim_frame_end
	nativedancer.globals.temp_frame_format = args.temp_frame_format
	nativedancer.globals.temp_frame_quality = args.temp_frame_quality
	nativedancer.globals.keep_temp = args.keep_temp
	# output creation
	nativedancer.globals.output_image_quality = args.output_image_quality
	nativedancer.globals.output_video_encoder = args.output_video_encoder
	nativedancer.globals.output_video_quality = args.output_video_quality
	nativedancer.globals.keep_fps = args.keep_fps
	nativedancer.globals.skip_audio = args.skip_audio
	# frame processors
	available_frame_processors = list_module_names('nativedancer/processors/frame/modules')
	nativedancer.globals.frame_processors = args.frame_processors
	for frame_processor in available_frame_processors:
		frame_processor_module = load_frame_processor_module(frame_processor)
		frame_processor_module.apply_args(program)
	# uis
	nativedancer.globals.ui_layouts = args.ui_layouts

	# face analyser
	nativedancer.globals.face_analyser_order = args.face_analyser_order
	nativedancer.globals.face_analyser_age = args.face_analyser_age
	nativedancer.globals.face_analyser_gender = args.face_analyser_gender
	nativedancer.globals.face_detector_model = args.face_detector_model
	nativedancer.globals.face_detector_size = args.face_detector_size
	nativedancer.globals.face_detector_score = args.face_detector_score
	# face selector
	nativedancer.globals.face_selector_mode = args.face_selector_mode
	nativedancer.globals.reference_face_position = args.reference_face_position
	nativedancer.globals.reference_face_distance = args.reference_face_distance
	nativedancer.globals.reference_frame_number = args.reference_frame_number
	# face mask
	nativedancer.globals.face_mask_blur = args.face_mask_blur
	nativedancer.globals.face_mask_padding = normalize_padding(args.face_mask_padding)


def run(program : ArgumentParser) -> None:
	apply_args(program)
	limit_resources()
	if not pre_check() or not content_analyser.pre_check() or not face_analyser.pre_check():
		return
	for frame_processor_module in get_frame_processors_modules(nativedancer.globals.frame_processors):
		if not frame_processor_module.pre_check():
			return
	if nativedancer.globals.headless:
		conditional_process()
	else:
		import nativedancer.uis.core as ui

		for ui_layout in ui.get_ui_layouts_modules(nativedancer.globals.ui_layouts):
			if not ui_layout.pre_check():
				return
		ui.launch()


def destroy() -> None:
	if nativedancer.globals.target_path:
		clear_temp(nativedancer.globals.target_path)
	sys.exit()


def limit_resources() -> None:
	if nativedancer.globals.max_memory:
		memory = nativedancer.globals.max_memory * 1024 ** 3
		if platform.system().lower() == 'darwin':
			memory = nativedancer.globals.max_memory * 1024 ** 6
		if platform.system().lower() == 'windows':
			import ctypes
			kernel32 = ctypes.windll.kernel32 # type: ignore[attr-defined]
			kernel32.SetProcessWorkingSetSize(-1, ctypes.c_size_t(memory), ctypes.c_size_t(memory))
		else:
			import resource
			resource.setrlimit(resource.RLIMIT_DATA, (memory, memory))


def pre_check() -> bool:
	if sys.version_info < (3, 9):
		update_status(helperdoc.get('python_not_supported').format(version = '3.9'))
		return False
	if not shutil.which('ffmpeg'):
		update_status(helperdoc.get('ffmpeg_not_installed'))
		return False
	return True


def conditional_process() -> None:
	for frame_processor_module in get_frame_processors_modules(nativedancer.globals.frame_processors):
		if not frame_processor_module.pre_process('output'):
			return
	if is_image(nativedancer.globals.target_path):
		process_image()
	if is_video(nativedancer.globals.target_path):
		process_video()


def process_image() -> None:
	if analyse_image(nativedancer.globals.target_path):
		return
	shutil.copy2(nativedancer.globals.target_path, nativedancer.globals.output_path)
	# process frame
	for frame_processor_module in get_frame_processors_modules(nativedancer.globals.frame_processors):
		update_status(helperdoc.get('processing'), frame_processor_module.NAME)
		frame_processor_module.process_image(nativedancer.globals.source_path, nativedancer.globals.output_path, nativedancer.globals.output_path)
		frame_processor_module.post_process()
	# compress image
	update_status(helperdoc.get('compressing_image'))
	if not compress_image(nativedancer.globals.output_path):
		update_status(helperdoc.get('compressing_image_failed'))
	# validate image
	if is_image(nativedancer.globals.output_path):
		update_status(helperdoc.get('processing_image_succeed'))
	else:
		update_status(helperdoc.get('processing_image_failed'))



def process_video() -> None:
	if analyse_video(nativedancer.globals.target_path, nativedancer.globals.trim_frame_start, nativedancer.globals.trim_frame_end):
		return
	fps = detect_fps(nativedancer.globals.target_path) if nativedancer.globals.keep_fps else 25.0
	nativedancer.globals.fps = fps
	# create temp
	update_status(helperdoc.get('creating_temp'))
	create_temp(nativedancer.globals.target_path)
	# extract frames
	update_status(helperdoc.get('extracting_frames_fps').format(fps = fps))
	
	extract_frames(nativedancer.globals.target_path, fps)
	# process frame
	temp_frame_paths = get_temp_frame_paths(nativedancer.globals.target_path)
	if temp_frame_paths:
		for frame_processor_module in get_frame_processors_modules(nativedancer.globals.frame_processors):
			update_status(helperdoc.get('processing'), frame_processor_module.NAME)
			frame_processor_module.pre_process(mode="output")
			frame_processor_module.process_video(nativedancer.globals.source_path, temp_frame_paths)
			frame_processor_module.post_process()
	else:
		update_status(helperdoc.get('temp_frames_not_found'))
		return
	
	## restore oringinal target path
	if nativedancer.globals.cached_path is not None:
		nativedancer.globals.target_path = nativedancer.globals.cached_path

	# merge video
	update_status(helperdoc.get('merging_video_fps').format(fps = fps))
	if not merge_video(nativedancer.globals.target_path, fps):
		update_status(helperdoc.get('merging_video_failed'))
		return
	# handle audio
	if nativedancer.globals.skip_audio:
		update_status(helperdoc.get('skipping_audio'))
		move_temp(nativedancer.globals.target_path, nativedancer.globals.output_path)
	else:
		update_status(helperdoc.get('restoring_audio'))
		if not restore_audio(nativedancer.globals.target_path, nativedancer.globals.output_path):
			update_status(helperdoc.get('restoring_audio_failed'))
			move_temp(nativedancer.globals.target_path, nativedancer.globals.output_path)
	# clear temp
	update_status(helperdoc.get('clearing_temp'))
	clear_temp(nativedancer.globals.target_path)
	# validate video
	if is_video(nativedancer.globals.output_path):
		update_status(helperdoc.get('processing_video_succeed'))
	else:
		update_status(helperdoc.get('processing_video_failed'))

def conditional_set_face_reference() -> None:
	if 'reference' in nativedancer.globals.face_selector_mode and not get_face_reference():
		if is_video(nativedancer.globals.target_path):
			reference_frame = get_video_frame(nativedancer.globals.target_path, nativedancer.globals.reference_frame_number)
		else:
			reference_frame = read_image(nativedancer.globals.target_path)
		reference_face = get_one_face(reference_frame, nativedancer.globals.reference_face_position)
		set_face_reference(reference_face)

def process_animate_video() -> None:
	import nativedancer.processors.frame.globals as frame_processors_globals
	if analyse_video(nativedancer.globals.target_path, nativedancer.globals.trim_frame_start, nativedancer.globals.trim_frame_end):
		return
	fps = detect_fps(nativedancer.globals.target_path) if nativedancer.globals.keep_fps else 25.0
	nativedancer.globals.fps = fps
	# create temp
	update_status(helperdoc.get('creating_temp'))
	create_temp(nativedancer.globals.target_path)
	# extract frames
	update_status(helperdoc.get('extracting_frames_fps').format(fps = fps))
	
	extract_frames(nativedancer.globals.target_path, fps)
	# process frame
	temp_frame_paths = get_temp_frame_paths(nativedancer.globals.target_path)
	if temp_frame_paths:
		for frame_processor_name in ['frame_pose', 'pose_frame']:
			frame_processor_module = load_frame_processor_module(frame_processor_name)
			update_status(helperdoc.get('processing'), frame_processor_module.NAME)
			frame_processor_module.pre_process(mode="output")
			frame_processor_module.process_video(nativedancer.globals.source_path, temp_frame_paths)
			frame_processor_module.post_process()
	else:
		update_status(helperdoc.get('temp_frames_not_found'))
		return
	
	## restore oringinal target path
	if nativedancer.globals.cached_path is not None:
		target_path = nativedancer.globals.cached_path

	# merge video
	update_status(helperdoc.get('merging_video_fps').format(fps = fps))
	if not merge_video(target_path, fps):
		update_status(helperdoc.get('merging_video_failed'))
		return
	# handle audio
	if nativedancer.globals.skip_audio:
		update_status(helperdoc.get('skipping_audio'))
		move_temp(target_path, frame_processors_globals.animate_path)
	else:
		update_status(helperdoc.get('restoring_audio'))
		if not restore_audio(target_path, frame_processors_globals.animate_path):
			update_status(helperdoc.get('restoring_audio_failed'))
			move_temp(target_path, frame_processors_globals.animate_path)


def process_facefusion_video() -> None:
	# process frame
	temp_frame_paths = get_temp_frame_paths(nativedancer.globals.cached_path)
	if temp_frame_paths:
		processes_list =  nativedancer.globals.frame_processors
		processes_list.remove("frame_pose")
		processes_list.remove("pose_frame")
		if processes_list.count == 0: return
		for frame_processor in processes_list:
			frame_processor_module = load_frame_processor_module(frame_processor)
			update_status(helperdoc.get('processing'), frame_processor_module.NAME)
			frame_processor_module.pre_process(mode="output")
			frame_processor_module.process_video(nativedancer.globals.source_path, temp_frame_paths)
			frame_processor_module.post_process()
	else:
		update_status(helperdoc.get('temp_frames_not_found'))
		return
	
	## restore oringinal target path
	if nativedancer.globals.cached_path is not None:
		nativedancer.globals.target_path = nativedancer.globals.cached_path

	# merge video
	update_status(helperdoc.get('merging_video_fps').format(fps = nativedancer.globals.fps))
	if not merge_video(nativedancer.globals.target_path, nativedancer.globals.fps):
		update_status(helperdoc.get('merging_video_failed'))
		return
	# handle audio
	if nativedancer.globals.skip_audio:
		update_status(helperdoc.get('skipping_audio'))
		move_temp(nativedancer.globals.target_path, nativedancer.globals.output_path)
	else:
		update_status(helperdoc.get('restoring_audio'))
		if not restore_audio(nativedancer.globals.target_path, nativedancer.globals.output_path):
			update_status(helperdoc.get('restoring_audio_failed'))
			move_temp(nativedancer.globals.target_path, nativedancer.globals.output_path)
	# clear temp
	update_status(helperdoc.get('clearing_temp'))
	clear_temp(nativedancer.globals.target_path)
	# validate video
	if is_video(nativedancer.globals.output_path):
		update_status(helperdoc.get('processing_video_succeed'))
	else:
		update_status(helperdoc.get('processing_video_failed'))
