VERSIONINFO =\
{
	'name': 'NativeDancer',
	'description': 'Dancing as your like as native dancer',
	'version': '0.1.0',
	'license': 'MIT',
	'author': 'AIFSH',
	'url': 'https://github.com/AIFSH/NativeDancer'
}


def get(key : str) -> str:
	return VERSIONINFO[key]
