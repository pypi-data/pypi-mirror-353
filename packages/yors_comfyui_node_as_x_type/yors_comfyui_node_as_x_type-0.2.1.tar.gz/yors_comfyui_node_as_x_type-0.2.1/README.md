<div align="center">
  <h1>yors_comfyui_node_as_x_type</h1>
  <p>
    <strong>🤖 some comfyui custom nodes to set it as known type.</strong>
  </p>
  
  ![PyPI - Version](https://img.shields.io/pypi/v/yors_comfyui_node_as_x_type)
  ![PyPI - License](https://img.shields.io/pypi/l/yors_comfyui_node_as_x_type)

</div>

## features

- feat(core): node to set it as any type
- feat(core): node to set it as image type
- feat(core): node to set it as model type
- feat(core): node to set it as clip type
- feat(core): node to set it as vae type
- feat(core): node to set it as conditioning type
- feat(core): node to set it as latent type
- feat(core): node to set it as string type
- feat(core): node to set it as int type
- feat(core): node to set it as float type
- feat(core): node to set it as number type

## 1 - install python package

```bash
pip install yors_comfyui_node_setup
pip install yors_comfyui_node_as_x_type
```

## 2 - use it in your python code

- in some comfyui custom nodes project or module

- code in `__init__.py`

```py
from yors_comfyui_node_setup import entry,node_install_requirements # global

# install requirements
node_install_requirements(__file__)

# export comfyui node vars
__all__,NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS,NODE_MENU_NAMES = entry(__name__,__file__)
```

## 3 - code yours nodes

- dirs map of your node may be:

```
.
└─__init__.py
└─nodes.py
```

- in any py file (no test in `__init__.py`)
- code nodes.py

```py
# base usage
from yors_comfyui_node_as_x_type import *

# # custom category ? do: (to test)
# all_class_in_this_module = get_classes_in_module(get_module(__name__))
# # all_class_in_this_module = get_classes_in_module(nodes)
# node_class_in_this_module=get_node_class(all_class_in_this_module)
# # log_node_class(node_class_in_this_module)
# set_node_class_category(node_class_in_this_module,"YMC/as_x_type")
# # log_node_class(node_class_in_this_module)
```

## Author

ymc-github <ymc.github@gmail.com>

## License

MIT
