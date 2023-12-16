import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from nativedancer import core

if __name__ == "__main__":
    core.cli()