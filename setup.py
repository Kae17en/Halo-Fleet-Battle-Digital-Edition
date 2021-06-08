from setuptools import setup

setup(
    name="HFB",
    options = {
        'build_apps': {
            'include_patterns': [
                '**/*.png',
                '**/*.jpg',
                '**/*.egg',
                '**/Assets/*',
                '**/*.py',
                '**/Scripts/*',
            ],
            'gui_apps': {
                'HFB': 'main.py',
            },
            'plugins': [
                'pandagl',
                'p3openal_audio',
                'p3ffmpeg',

            ],
            'platforms': [
                'win32',
                'win_amd64',
            ],
        }
    }
)