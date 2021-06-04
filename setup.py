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
            ],
            'gui_apps': {
                'HFB': 'main.py',
            },
            'plugins': [
                'pandagl',
                'p3openal_audio',
                'p3ffmpeg',

            ],
            'plateforms': [
                'win32',
                'win_amd64',
            ],
        }
    }
)