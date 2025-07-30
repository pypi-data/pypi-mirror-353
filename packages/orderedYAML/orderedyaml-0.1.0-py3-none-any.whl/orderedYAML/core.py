"""
A utility class for recursively converting nested Python dictionaries and lists
into ordered, block-style YAML using `ruamel.yaml`, with support for custom key ordering.

This module defines the `OrderedYAML` class, which encapsulates YAML transformation
and dumping functionality without exposing internal conversion logic.
"""
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from typing import Any, Dict, List, Tuple, Union
import sys
import io

YAMLData = Union[dict, list, str, int, float, bool, None]
Path = Tuple[str, ...]

class OrderedYAML:
    """
    Convert and render nested Python data into ordered, structured YAML
    using `ruamel.yaml.CommentedMap`, supporting customizable key order.

    Attributes:
        data (YAMLData): The transformed YAML-ready data with ordered keys.
    """
    def __init__(self, raw_data: YAMLData, key_ordering: Dict[Path, List[str]] = None):
        """
        Initialize the OrderedYAML object with raw data and optional key ordering.

        Args:
            raw_data (YAMLData): The input data to be transformed (dict, list, etc.).
            key_ordering (Dict[Tuple[str, ...], List[str]], optional):
                A mapping of tuple paths to key orderings. For example:
                {
                    (): ['apiVersion', 'kind', 'metadata', 'spec'],
                    ('metadata',): ['name', 'labels']
                }
                Defaults to preserving Python dict insertion order.
        """
        self._yaml = YAML()
        self._yaml.default_flow_style = False
        self._yaml.indent(mapping=2, sequence=4, offset=2)

        self.data = self._to_ordered_commented_map(raw_data, key_ordering or {}, ())

    def _to_ordered_commented_map(
        self, data: YAMLData, key_orders: Dict[Path, List[str]], path: Path
    ) -> YAMLData:
        """
        Recursively transform dicts into CommentedMaps with optional key ordering.

        Args:
            data (YAMLData): The input data to transform.
            key_orders (Dict[Path, List[str]]): Key ordering rules by nested path.
            path (Path): Internal recursive path tracker.

        Returns:
            YAMLData: The transformed data as a CommentedMap or list.
        """
        if isinstance(data, dict):
            cm = CommentedMap()
            desired_order = key_orders.get(path, [])

            for key in desired_order:
                if key in data:
                    cm[key] = self._to_ordered_commented_map(data[key], key_orders, path + (key,))
            for key in data:
                if key not in cm:
                    cm[key] = self._to_ordered_commented_map(data[key], key_orders, path + (key,))
            return cm

        elif isinstance(data, list):
            return [self._to_ordered_commented_map(item, key_orders, path) for item in data]

        else:
            return data

    def dump(self, file=None):
        """
        Dump the ordered YAML to a file-like object (defaults to sys.stdout).

        Args:
            file (file-like, optional): An open writable file-like object.
        """
        self._yaml.dump(self.data, file or sys.stdout)

    def dumps(self) -> str:
        """
        Return the ordered YAML as a string.

        Returns:
            str: The YAML representation of the transformed data.
        """
        buf = io.StringIO()
        self._yaml.dump(self.data, buf)
        return buf.getvalue()
