from typing import Optional
import gradio

from nativedancer import versioninfo, helperdoc

ABOUT_BUTTON : Optional[gradio.HTML] = None
DONATE_BUTTON : Optional[gradio.HTML] = None


def render() -> None:
	global ABOUT_BUTTON
	global DONATE_BUTTON

	ABOUT_BUTTON = gradio.Button(
		value = versioninfo.get('name') + ' ' + versioninfo.get('version'),
		variant = 'primary',
		link = versioninfo.get('url')
	)
	DONATE_BUTTON = gradio.Button(
		value = helperdoc.get('donate_button_label'),
		link = versioninfo.get('url'),
		size = 'sm'
	)
