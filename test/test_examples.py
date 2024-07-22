import xml.etree.ElementTree as ET
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

import pytest
from qrSVG.image import svg2pil
from qrSVG.qr import QR
from qrSVG.validate import read


@pytest.mark.parametrize(
    "example",
    [
        pytest.param(
            path,
            id=path.stem,
        )
        for path in Path(__file__).parent.with_name("examples").glob("*.py")
    ],
)
def test_example(example, monkeypatch, tmp_path):
    """Run all the examples and validate that they work."""
    sentinel = False  # Used to check that the mock was called
    tmp_path.mkdir(parents=True, exist_ok=True)

    def mock_save(self, output):
        nonlocal sentinel
        sentinel = True
        tmp = tmp_path / output.name
        tmp.write_bytes(ET.tostring(self.tree, xml_declaration=True))
        assert self._data == read(svg2pil(tmp, 2048, 2048))

    # Patch save method to validate the output
    monkeypatch.setattr(QR, "save", mock_save)

    # Get the module/example
    loader = SourceFileLoader(f"example.{example.stem}", str(example))
    spec = spec_from_loader(loader.name, loader)
    assert spec, "Failed to create module spec"
    module = module_from_spec(spec)

    # Execute the module/example
    loader.exec_module(module)
    assert sentinel, "Save method was never called"
