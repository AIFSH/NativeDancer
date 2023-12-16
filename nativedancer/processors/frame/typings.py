from typing import Literal

PoseFrameModel = Literal['MagicAnimate']
FramePoseModel = Literal['DensePose']
FrameEnhancerModel = Literal['real_esrgan_x2plus', 'real_esrgan_x4plus', 'real_esrnet_x4plus']
FaceSwapperModel = Literal['blendface_256', 'inswapper_128', 'inswapper_128_fp16', 'simswap_256', 'simswap_512_unofficial']
FaceEnhancerModel = Literal['codeformer', 'gfpgan_1.2', 'gfpgan_1.3', 'gfpgan_1.4', 'gpen_bfr_256', 'gpen_bfr_512', 'restoreformer']
FaceDebuggerItem = Literal['bbox', 'kps', 'face-mask', 'score']
