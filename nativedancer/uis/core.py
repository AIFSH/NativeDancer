from typing import Dict, Optional, Any, List
from types import ModuleType
import importlib
import sys
import gradio
from nativedancer import helperdoc

import nativedancer.globals
from nativedancer import versioninfo
from nativedancer.uis.typing import Component, ComponentName
from nativedancer.utils import resolve_relative_path

UI_COMPONENTS: Dict[ComponentName, Component] = {}
UI_LAYOUT_MODULES : List[ModuleType] = []
UI_LAYOUT_METHODS =\
[
	'pre_check',
	'pre_render',
	'render',
	'listen',
	'run'
]


def load_ui_layout_module(ui_layout : str) -> Any:
	try:
		ui_layout_module = importlib.import_module('nativedancer.uis.layouts.' + ui_layout)
		for method_name in UI_LAYOUT_METHODS:
			if not hasattr(ui_layout_module, method_name):
				raise NotImplementedError
	except ModuleNotFoundError:
		sys.exit(helperdoc.get('ui_layout_not_loaded').format(ui_layout = ui_layout))
	except NotImplementedError:
		sys.exit(helperdoc.get('ui_layout_not_implemented').format(ui_layout = ui_layout))
	return ui_layout_module


def get_ui_layouts_modules(ui_layouts : List[str]) -> List[ModuleType]:
	global UI_LAYOUT_MODULES

	if not UI_LAYOUT_MODULES:
		for ui_layout in ui_layouts:
			ui_layout_module = load_ui_layout_module(ui_layout)
			UI_LAYOUT_MODULES.append(ui_layout_module)
	return UI_LAYOUT_MODULES


def get_ui_component(name : ComponentName) -> Optional[Component]:
	if name in UI_COMPONENTS:
		return UI_COMPONENTS[name]
	return None


def register_ui_component(name : ComponentName, component: Component) -> None:
	UI_COMPONENTS[name] = component


def launch() -> None:
	with gradio.Blocks(theme = get_theme(), css = get_css(), title = versioninfo.get('name') + ' ' + versioninfo.get('version')) as ui:
		for ui_layout in nativedancer.globals.ui_layouts:
			ui_layout_module = load_ui_layout_module(ui_layout)
			if ui_layout_module.pre_render():
				ui_layout_module.render()
				ui_layout_module.listen()

	for ui_layout in nativedancer.globals.ui_layouts:
		ui_layout_module = load_ui_layout_module(ui_layout)
		ui_layout_module.run(ui)


def get_theme() -> gradio.Theme:
	return gradio.themes.Base(
		primary_hue = gradio.themes.colors.purple,
		secondary_hue = gradio.themes.colors.neutral,
		font = gradio.themes.GoogleFont('Open Sans')
	).set(
		background_fill_primary = '*neutral_100',
		block_background_fill = 'white',
		block_border_width = '0',
		block_label_background_fill = '*primary_100',
		block_label_background_fill_dark = '*primary_600',
		block_label_border_width = 'none',
		block_label_margin = '0.5rem',
		block_label_radius = '*radius_md',
		block_label_text_color = '*primary_500',
		block_label_text_color_dark = 'white',
		block_label_text_weight = '600',
		block_title_background_fill = '*primary_100',
		block_title_background_fill_dark = '*primary_600',
		block_title_padding = '*block_label_padding',
		block_title_radius = '*block_label_radius',
		block_title_text_color = '*primary_500',
		block_title_text_size = '*text_sm',
		block_title_text_weight = '600',
		block_padding = '0.5rem',
		border_color_primary = 'transparent',
		border_color_primary_dark = 'transparent',
		button_large_padding = '2rem 0.5rem',
		button_large_text_weight = 'normal',
		button_primary_background_fill = '*primary_500',
		button_primary_text_color = 'white',
		button_secondary_background_fill = 'white',
		button_secondary_border_color = 'transparent',
		button_secondary_border_color_dark = 'transparent',
		button_secondary_border_color_hover = 'transparent',
		button_secondary_border_color_hover_dark = 'transparent',
		button_secondary_text_color = '*neutral_800',
		button_small_padding = '0.75rem',
		checkbox_background_color = '*neutral_200',
		checkbox_background_color_selected = '*primary_600',
		checkbox_background_color_selected_dark = '*primary_700',
		checkbox_border_color_focus = '*primary_500',
		checkbox_border_color_focus_dark = '*primary_600',
		checkbox_border_color_selected = '*primary_600',
		checkbox_border_color_selected_dark = '*primary_700',
		checkbox_label_background_fill = '*neutral_50',
		checkbox_label_background_fill_hover = '*neutral_50',
		checkbox_label_background_fill_selected = '*primary_500',
		checkbox_label_background_fill_selected_dark = '*primary_600',
		checkbox_label_text_color_selected = 'white',
		input_background_fill = '*neutral_50',
		shadow_drop = 'none',
		slider_color = '*primary_500',
		slider_color_dark = '*primary_600'
	)


def get_css() -> str:
	fixes_css_path = resolve_relative_path('uis/assets/fixes.css')
	overrides_css_path = resolve_relative_path('uis/assets/overrides.css')
	return open(fixes_css_path, 'r').read() + open(overrides_css_path, 'r').read()
