from typing import Dict, Tuple
import subprocess
from argparse import ArgumentParser, HelpFormatter
from nativedancer import helperdoc,versioninfo

subprocess.call([ 'pip', 'install' , 'inquirer', '-q' ])

import inquirer

TORCH : Dict[str, str] =\
{
	'default': 'default',
	'cpu': 'cpu',
	'cuda': 'cu121',
	'rocm': 'rocm5.6'
}

ONNXRUNTIMES : Dict[str, Tuple[str, str]] =\
{
	'default': ('onnxruntime', '1.16.3'),
	'cuda': ('onnxruntime-gpu', '1.16.3'),
	'coreml-legacy': ('onnxruntime-coreml', '1.13.1'),
	'coreml-silicon': ('onnxruntime-silicon', '1.16.0'),
	'directml': ('onnxruntime-directml', '1.16.3'),
	'openvino': ('onnxruntime-openvino', '1.16.0')
}

def cli() -> None:
	program = ArgumentParser(formatter_class = lambda prog: HelpFormatter(prog, max_help_position = 120))
	program.add_argument('--torch', help = helperdoc.get('install_dependency_help').format(dependency = 'torch'), dest = 'torch', choices = TORCH.keys())
	program.add_argument('--onnxruntime', help = helperdoc.get('install_dependency_help').format(dependency = 'onnxruntime'), dest = 'onnxruntime', choices = ONNXRUNTIMES.keys())
	program.add_argument('-v', '--version', version = versioninfo.get('name') + ' ' + versioninfo.get('version'), action = 'version')
	run(program)


def run(program : ArgumentParser) -> None:
	args = program.parse_args()

	if args.torch and args.onnxruntime:
		answers =\
		{
			'torch': args.torch,
			'onnxruntime': args.onnxruntime
		}
	else:
		answers = inquirer.prompt(
		[
			inquirer.List('torch', message = helperdoc.get('install_dependency_help').format(dependency = 'torch'), choices = list(TORCH.keys())),
			inquirer.List('onnxruntime', message = helperdoc.get('install_dependency_help').format(dependency = 'onnxruntime'), choices = list(ONNXRUNTIMES.keys()))
		])
	if answers:
		torch = answers['torch']
		torch_wheel = TORCH[torch]
		onnxruntime = answers['onnxruntime']
		onnxruntime_name, onnxruntime_version = ONNXRUNTIMES[onnxruntime]
		subprocess.call(['pip', 'install', 'basicsr', '--use-pep517', '--verbose'])
		subprocess.call([ 'pip', 'uninstall', 'torch', '-y' ])
		if torch_wheel == 'default':
			subprocess.call([ 'pip', 'install', '-r', 'requirements.txt' ,'--verbose'])
		else:
			subprocess.call([ 'pip', 'install', '-r', 'requirements.txt', '--verbose','--extra-index-url', 'https://download.pytorch.org/whl/' + torch_wheel ])
		subprocess.call([ 'pip', 'uninstall', 'onnxruntime', onnxruntime_name, '-y' ])
		subprocess.call([ 'pip', 'install', onnxruntime_name + '==' + onnxruntime_version ])
		subprocess.call(['apt', 'update'])
		subprocess.call(['apt','install', 'ffmpeg'])
