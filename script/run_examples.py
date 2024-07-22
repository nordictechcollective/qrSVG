"""
Run examples to ensure their output is up-to-date.
"""

from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

examples = Path(__file__).parent.with_name("examples").glob("*.py")

for example in examples:
    loader = SourceFileLoader(f"example.{example.stem}", str(example))

    # Some extra hoops as load_module will soon be deprecated
    spec = spec_from_loader(loader.name, loader)
    assert spec, f"Failed to create module spec for {example.name!r}"
    module = module_from_spec(spec)

    loader.exec_module(module)
