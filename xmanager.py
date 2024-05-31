"""A simple experiment manager in a single Python file."""

import os
import sys
import pathlib
import shutil
import json
import numpy as np
from typing import Dict, Any
from datetime import datetime


class XManager:
    """Manager for experiments.

    Examples
    --------
 
    ```python
    # Initialize.
    # This will generate a path `experiments/1/<datetime>/`.
    # It will also copy this script to ``experiments/1/<datetime>/source.py`,
    # except for REPL mode, where script cannot be copied.
    xm = XManager('experiments', '1')

    # Add parameters.
    xm.config_1 = ...
    # and after experiments, log the results.
    xm.result_1 = ...
    xm.result_2 = ...

    # The `get_path` method can give you a path to save something,
    # such as path to model checkpoint.
    # For example, save figure to `experiments/<datetime>/figures/my_plot.png`.
    plt.savefig(xm.get_path('figures', 'my_plot.png'))

    # Save parameters to `experiments/<datetime>/params.json`
    # The parameters are those assigned by `xm.<param> = <value>`.
    xm.save_params()
    ```
    """

    def __init__(self, *base_dir: str):
        base_dir = os.path.join(*base_dir)

        self.x_dir = os.path.join(
            os.path.abspath(base_dir),
            datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
        )
        XManager._ensure_dir(self.x_dir)

        # If in RELP, sys.argv[0] will be empty.
        if sys.argv[0]:
            script_path = os.path.realpath(sys.argv[0])
            shutil.copy(script_path, self.get_path('source.py'))

    @classmethod
    def _is_dir(cls, path: str):
        """Determines if it is a folder by checking file extension."""
        ext = os.path.splitext(path)[-1]
        # If it is a folder, ext is an empty string (i.e. '').
        return True if ext == '' else False

    @classmethod
    def _ensure_dir(cls, path: str):
        if cls._is_dir(path):
            dir_path = path
        else:
            dir_path = os.path.dirname(path)
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True) 

    def get_path(self, *file_or_dir: str, ensure_dir=True):
        """
        Args:
            file_or_dir (str): Relative path to a file or directory.
            ensure_dir (bool, optional): When it is a directory but does not
                exist, create one if `ensure_dir` is true.

        Returns:
            str: The absolute path to the `file_or_dir`.
        """
        path = os.path.join(self.x_dir, *file_or_dir)
        if ensure_dir:
            self._ensure_dir(path)
        return path

    @classmethod
    def jsonfy(cls, x):
        """Auxiliary class method for JSONfying an object x.
        
        Args:
            x (object): Being any type of object.

        Returns:
            dict: The JSON dictionary.
        
        Raises:
            TypeError: When non JSON-serializable object is met.
        """
        # np.ndarray is not JSON serializable.
        if isinstance(x, np.ndarray):
            return x.tolist()
        if isinstance(x, dict):
            return {
                k: XManager.jsonfy(v)
                for k, v in x.items()
            }
        if isinstance(x, (list, tuple)):
            return [XManager.jsonfy(xi) for xi in x]
        # TODO: convert other objects which are not JSON serializable.
        if not hasattr(x, '__dict__'):
            # Check serializablility.
            try:
                json.dumps(x)
            except TypeError:
                raise TypeError(f'Type "{type(x)}" is not JSON-serializable.')
            return x
 
        json_dict : Dict[str, Any] = {}
        for k, v in x.__dict__.items():
            json_dict[k] = XManager.jsonfy(v)
        return json_dict

    def get_params(self):
        params = XManager.jsonfy(self)
        del params['x_dir']
        return params

    def save_params(self):
        """Save the parameters as JSON to `params.json`."""
        with open(self.get_path('params.json'), 'w') as f:
            json.dump(self.get_params(), f, indent=2)
