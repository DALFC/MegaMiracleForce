import UnityPy, os, json, math
from PIL import Image

def Extract(filename):
	env = UnityPy.load(filename)
	js = None
	img = None
	for obj in env.objects:
		if obj.type.name in ["Texture2D", "Sprite"]:
			data = obj.read()
			dest = os.path.join("out", data.name)
			img = data.image
		if obj.type.name == "MonoBehaviour":
			data = obj.read()
			if obj.serialized_type.nodes:
				tree = obj.read_typetree()
				fp = os.path.join("out", f"{data.name}.json")
				js = tree
			else:
				print("Weird")

	cellSize = js["cellSize"]
	padding = js["padding"]
	paddingCellSize = cellSize - padding * 2;
	textureDataList = js["textureDataList"]
	width, height = img.size
	atlasCellCountX = math.ceil(width / cellSize)
	atlasCellCountY = math.ceil(height / cellSize)

	cells = []
	for y in range(atlasCellCountY - 1, -1, -1):
		for x in range(atlasCellCountX):
			c = img.crop((x * cellSize, y * cellSize, (x + 1) * cellSize, (y + 1) * cellSize))
			c = c.crop((padding, padding, padding + paddingCellSize, padding + paddingCellSize))
			cells.append(c)

	for tex in textureDataList:
		cellX = math.ceil(tex["width"] / paddingCellSize)
		cellY = math.ceil(tex["height"] / paddingCellSize)
		coords = [(xb*paddingCellSize, tex["height"] - (yb+1)*paddingCellSize, (xb+1)*paddingCellSize, tex["height"] - (yb)*paddingCellSize)
				 for yb in range(cellY) for xb in range(cellX)]

		result = Image.new(img.mode, (tex["width"], tex["height"]))
		count = 0
		for cellIndex in tex["cellIndexList"]:
			count += 1
			if cellIndex == 0:
				continue
			result.paste(cells[cellIndex], coords[count - 1])
		dest = os.path.splitext(filename)[0]
		os.makedirs(dest, exist_ok = True)
		result.save(os.path.join(dest, tex["name"] + ".png"))
