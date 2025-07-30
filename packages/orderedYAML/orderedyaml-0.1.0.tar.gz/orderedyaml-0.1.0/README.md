# orderedYAML
A small Python package to recursively convert Python dicts/lists into `ruamel.yaml`-compatible, ordered YAML using `CommentedMap`. Preserves formatting, ordering, and supports custom key orders at any nesting depth.

## Features

- Recursively reorders YAML dictionaries based on custom paths
- Outputs block-style YAML using `ruamel.yaml`
- Compatible with Python 3.7+

## Installation

```bash
pip install yaml-order
```

---
## Usage
```python
from orderedYAML import OrderedYAML

data = {
    'metadata': {
        'labels': {'env': 'prod', 'app': 'my-app'},
        'name': 'my-resource',
    },
    'apiVersion': 'v1',
    'kind': 'Service',
    'spec': {
        'ports': [{'port': 80}],
        'selector': {'app': 'my-app'},
        'type': 'ClusterIP',
    },
}

ordering = {
    (): ['apiVersion', 'kind', 'metadata', 'spec'],
    ('metadata',): ['name', 'labels'],
    ('spec',): ['selector', 'ports', 'type'],
}

yaml_obj = OrderedYAML(data, ordering)

# To stdout
yaml_obj.dump()

# Or to a file
with open("out.yaml", "w") as f:
    yaml_obj.dump(f)

# Or get as a string
yaml_string = yaml_obj.dumps()
```