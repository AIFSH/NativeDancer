from typing import List
import numpy

from nativedancer.processors.frame.typings import *

frame_pose_models : List[FramePoseModel] = [ 'DensePose' ]
pose_frame_models : List[PoseFrameModel] = [ 'MagicAnimate' ]
frame_enhancer_models : List[FrameEnhancerModel] = [ 'real_esrgan_x2plus', 'real_esrgan_x4plus', 'real_esrnet_x4plus' ]
frame_enhancer_blend_range : List[int] = numpy.arange(0, 101, 1).tolist()

face_swapper_models : List[FaceSwapperModel] = [ 'blendface_256', 'inswapper_128', 'inswapper_128_fp16', 'simswap_256', 'simswap_512_unofficial' ]
face_enhancer_models : List[FaceEnhancerModel] = [ 'codeformer', 'gfpgan_1.2', 'gfpgan_1.3', 'gfpgan_1.4', 'gpen_bfr_256', 'gpen_bfr_512', 'restoreformer' ]
face_debugger_items : List[FaceDebuggerItem] = [ 'bbox', 'kps', 'face-mask', 'score' ]
face_enhancer_blend_range : List[int] = numpy.arange(0, 101, 1).tolist()
