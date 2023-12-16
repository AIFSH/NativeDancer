from typing import Optional

import gradio

import nativedancer.globals
import nativedancer.choices
from nativedancer import helperdoc
from nativedancer.typing import FaceAnalyserOrder, FaceAnalyserAge, FaceAnalyserGender, FaceDetectorModel
from nativedancer.uis.core import register_ui_component

FACE_ANALYSER_ORDER_DROPDOWN : Optional[gradio.Dropdown] = None
FACE_ANALYSER_AGE_DROPDOWN : Optional[gradio.Dropdown] = None
FACE_ANALYSER_GENDER_DROPDOWN : Optional[gradio.Dropdown] = None
FACE_DETECTOR_SIZE_DROPDOWN : Optional[gradio.Dropdown] = None
FACE_DETECTOR_SCORE_SLIDER : Optional[gradio.Slider] = None
FACE_DETECTOR_MODEL_DROPDOWN : Optional[gradio.Dropdown] = None


def render() -> None:
	global FACE_ANALYSER_ORDER_DROPDOWN
	global FACE_ANALYSER_AGE_DROPDOWN
	global FACE_ANALYSER_GENDER_DROPDOWN
	global FACE_DETECTOR_SIZE_DROPDOWN
	global FACE_DETECTOR_SCORE_SLIDER
	global FACE_DETECTOR_MODEL_DROPDOWN

	with gradio.Row():
		FACE_ANALYSER_ORDER_DROPDOWN = gradio.Dropdown(
			label = helperdoc.get('face_analyser_order_dropdown_label'),
			choices = nativedancer.choices.face_analyser_orders,
			value = nativedancer.globals.face_analyser_order
		)
		FACE_ANALYSER_AGE_DROPDOWN = gradio.Dropdown(
			label = helperdoc.get('face_analyser_age_dropdown_label'),
			choices = [ 'none' ] + nativedancer.choices.face_analyser_ages,
			value = nativedancer.globals.face_analyser_age or 'none'
		)
		FACE_ANALYSER_GENDER_DROPDOWN = gradio.Dropdown(
			label = helperdoc.get('face_analyser_gender_dropdown_label'),
			choices = [ 'none' ] + nativedancer.choices.face_analyser_genders,
			value = nativedancer.globals.face_analyser_gender or 'none'
		)
	FACE_DETECTOR_MODEL_DROPDOWN = gradio.Dropdown(
		label = helperdoc.get('face_detector_model_dropdown_label'),
		choices = nativedancer.choices.face_detector_models,
		value = nativedancer.globals.face_detector_model
	)
	FACE_DETECTOR_SIZE_DROPDOWN = gradio.Dropdown(
		label = helperdoc.get('face_detector_size_dropdown_label'),
		choices = nativedancer.choices.face_detector_sizes,
		value = nativedancer.globals.face_detector_size
	)
	FACE_DETECTOR_SCORE_SLIDER = gradio.Slider(
		label = helperdoc.get('face_detector_score_slider_label'),
		value = nativedancer.globals.face_detector_score,
		step =nativedancer.choices.face_detector_score_range[1] - nativedancer.choices.face_detector_score_range[0],
		minimum = nativedancer.choices.face_detector_score_range[0],
		maximum = nativedancer.choices.face_detector_score_range[-1]
	)
	register_ui_component('face_analyser_order_dropdown', FACE_ANALYSER_ORDER_DROPDOWN)
	register_ui_component('face_analyser_age_dropdown', FACE_ANALYSER_AGE_DROPDOWN)
	register_ui_component('face_analyser_gender_dropdown', FACE_ANALYSER_GENDER_DROPDOWN)
	register_ui_component('face_detector_model_dropdown', FACE_DETECTOR_MODEL_DROPDOWN)
	register_ui_component('face_detector_size_dropdown', FACE_DETECTOR_SIZE_DROPDOWN)
	register_ui_component('face_detector_score_slider', FACE_DETECTOR_SCORE_SLIDER)


def listen() -> None:
	FACE_ANALYSER_ORDER_DROPDOWN.select(update_face_analyser_order, inputs = FACE_ANALYSER_ORDER_DROPDOWN)
	FACE_ANALYSER_AGE_DROPDOWN.select(update_face_analyser_age, inputs = FACE_ANALYSER_AGE_DROPDOWN)
	FACE_ANALYSER_GENDER_DROPDOWN.select(update_face_analyser_gender, inputs = FACE_ANALYSER_GENDER_DROPDOWN)
	FACE_DETECTOR_MODEL_DROPDOWN.change(update_face_detector_model, inputs = FACE_DETECTOR_MODEL_DROPDOWN)
	FACE_DETECTOR_SIZE_DROPDOWN.select(update_face_detector_size, inputs = FACE_DETECTOR_SIZE_DROPDOWN)
	FACE_DETECTOR_SCORE_SLIDER.change(update_face_detector_score, inputs = FACE_DETECTOR_SCORE_SLIDER)


def update_face_analyser_order(face_analyser_order : FaceAnalyserOrder) -> None:
	nativedancer.globals.face_analyser_order = face_analyser_order if face_analyser_order != 'none' else None


def update_face_analyser_age(face_analyser_age : FaceAnalyserAge) -> None:
	nativedancer.globals.face_analyser_age = face_analyser_age if face_analyser_age != 'none' else None


def update_face_analyser_gender(face_analyser_gender : FaceAnalyserGender) -> None:
	nativedancer.globals.face_analyser_gender = face_analyser_gender if face_analyser_gender != 'none' else None


def update_face_detector_model(face_detector_model : FaceDetectorModel) -> None:
	nativedancer.globals.face_detector_model = face_detector_model


def update_face_detector_size(face_detector_size : str) -> None:
	nativedancer.globals.face_detector_size = face_detector_size


def update_face_detector_score(face_detector_score : float) -> None:
	nativedancer.globals.face_detector_score = face_detector_score
