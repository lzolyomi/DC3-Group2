import os
import platform

def locate_data_(file = None, stored_local=False):
    """Returns the directory where the data file is located."""

    current_wd = os.path.abspath(os.getcwd())
    if platform.system() == 'Windows':
        data_dir = '''\\data'''
        hash_slinging_slasher = '''\\'''
    else:
        data_dir = '''/data'''
        hash_slinging_slasher = '''/'''
    while not os.path.exists(current_wd + data_dir):
        if current_wd.rfind(hash_slinging_slasher) == -1:
            raise Exception('/data directory not found. Please store csv files in same folder as current file'
                            'and set value of stored_local back to True (default value with no input).')
        current_wd = current_wd[:current_wd.rfind(hash_slinging_slasher)]
    current_wd = current_wd + data_dir
    if stored_local:
        return os.path.abspath(os.getcwd())
    else:
        if file is not None:
            return current_wd + hash_slinging_slasher + file
        else:
            return current_wd

def correct_slash():
    """Returns the system specific correct slash"""
    if platform.system() == 'Windows':
        s = '''\\'''
    else:
        s = "/"
    return s 

def map_settings():
    config = {'version': 'v1',
 'config': {'visState': {'filters': [],
   'layers': [{'id': 'xgapbz',
     'type': 'point',
     'config': {'dataId': 'data_1',
      'label': 'new layer',
      'color': [255, 203, 153],
      'highlightColor': [252, 242, 26, 255],
      'columns': {'lat': 'lat', 'lng': 'long', 'altitude': None},
      'isVisible': True,
      'visConfig': {'radius': 10,
       'fixedRadius': False,
       'opacity': 0.8,
       'outline': False,
       'thickness': 2,
       'strokeColor': None,
       'colorRange': {'name': 'Global Warming',
        'type': 'sequential',
        'category': 'Uber',
        'colors': ['#5A1846',
         '#900C3F',
         '#C70039',
         '#E3611C',
         '#F1920E',
         '#FFC300']},
       'strokeColorRange': {'name': 'Global Warming',
        'type': 'sequential',
        'category': 'Uber',
        'colors': ['#5A1846',
         '#900C3F',
         '#C70039',
         '#E3611C',
         '#F1920E',
         '#FFC300']},
       'radiusRange': [0, 50],
       'filled': True},
      'hidden': False,
      'textLabel': [{'field': None,
        'color': [255, 255, 255],
        'size': 18,
        'offset': [0, 0],
        'anchor': 'start',
        'alignment': 'center'}]},
     'visualChannels': {'colorField': None,
      'colorScale': 'quantile',
      'strokeColorField': None,
      'strokeColorScale': 'quantile',
      'sizeField': None,
      'sizeScale': 'linear'}}],
   'interactionConfig': {'tooltip': {'fieldsToShow': {'data_1': [{'name': 'Unnamed: 0',
        'format': None},
       {'name': 'objectid', 'format': None},
       {'name': 'code', 'format': None},
       {'name': 'X', 'format': None},
       {'name': 'Y', 'format': None}]},
     'compareMode': False,
     'compareType': 'absolute',
     'enabled': True},
    'brush': {'size': 0.5, 'enabled': False},
    'geocoder': {'enabled': False},
    'coordinate': {'enabled': False}},
   'layerBlending': 'normal',
   'splitMaps': [],
   'animationConfig': {'currentTime': None, 'speed': 1}},
  'mapState': {'bearing': 0,
   'dragRotate': False,
   'latitude': 52.01689538181023,
   'longitude': 5.4140818488043205,
   'pitch': 0,
   'zoom': 9.177299864935193,
   'isSplit': False},
  'mapStyle': {'styleType': 'dark',
   'topLayerGroups': {},
   'visibleLayerGroups': {'label': True,
    'road': True,
    'border': False,
    'building': True,
    'water': True,
    'land': True,
    '3d building': False},
   'threeDBuildingColor': [9.665468314072013,
    17.18305478057247,
    31.1442867897876],
   'mapStyles': {}}}}
    return config
