"""
This file records the directory paths to the different datasets.
You will need to configure it for training the model.

All datasets follows the following format, where fgr and pha points to directory that contains jpg or png.
Inside the directory could be any nested formats, but fgr and pha structure must match. You can add your own
dataset to the list as long as it follows the format. 'fgr' should point to foreground images with RGB channels,
'pha' should point to alpha images with only 1 grey channel.
{
    'YOUR_DATASET': {
        'train': {
            'fgr': 'PATH_TO_IMAGES_DIR',
            'pha': 'PATH_TO_IMAGES_DIR',
        },
        'valid': {
            'fgr': 'PATH_TO_IMAGES_DIR',
            'pha': 'PATH_TO_IMAGES_DIR',
        }
    }
}
"""

DATA_PATH = {
    'videomatte240k': {
        'train': {
            'fgr': './VideoMatte240K_JPEG_HD/train/fgr/',
            'pha': './VideoMatte240K_JPEG_HD/train/pha/'
        },
        'valid': {
            'fgr': './VideoMatte240K_JPEG_HD/test/fgr/',
            'pha': './VideoMatte240K_JPEG_HD/test/pha/'
        }
    },
    'photomatte13k': {
        'train': {
            'fgr': './PhotoMatte85/fgr/',
            'pha': './PhotoMatte85/pha/'
        },
        'valid': {
            'fgr': './PhotoMatte85/fgr/',
            'pha': './PhotoMatte85/pha/'
        }
    },
    'distinction': {
        'train': {
            'fgr': 'PATH_TO_IMAGES_DIR',
            'pha': 'PATH_TO_IMAGES_DIR',
        },
        'valid': {
            'fgr': 'PATH_TO_IMAGES_DIR',
            'pha': 'PATH_TO_IMAGES_DIR'
        },
    },
    'adobe': {
        'train': {
            'fgr': 'PATH_TO_IMAGES_DIR',
            'pha': 'PATH_TO_IMAGES_DIR',
        },
        'valid': {
            'fgr': 'PATH_TO_IMAGES_DIR',
            'pha': 'PATH_TO_IMAGES_DIR'
        },
    },
    'PhotoMatte85': {
        'train': {
            'fgr': './PhotoMatte85/fgr/',
            'pha': './PhotoMatte85/pha/',
        },
        'valid': {
            'fgr': 'PATH_TO_IMAGES_DIR',
            'pha': 'PATH_TO_IMAGES_DIR'
        },
    },
    'backgrounds': {
        'train': './Backgrounds/',
        'valid': './Backgrounds/'
    },
    'stuff': {
        'train': {
            'fgr': './stuff/fgr/',
            'pha': './stuff/pha/'
        },
        'valid': {
            'fgr': './stuff/fgr/',
            'pha': './stuff/pha/'
        }
    },
}