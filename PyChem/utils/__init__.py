def getByPath(root, path):
	cur = root
	for el in path.split("."):
		cur = getattr(cur, el)
	return cur
