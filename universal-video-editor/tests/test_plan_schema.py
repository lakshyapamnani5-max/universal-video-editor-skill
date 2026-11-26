import json, pathlib
p=pathlib.Path(__file__).parents[1]/"templates"/"edit.example.json"
data=json.loads(p.read_text())
assert data["clips"] and data["output"]["width"] > 0
assert data["output"]["height"] > 0
print("UVE plan schema smoke test passed")
