freeBlockList = set([i for i in range(1, 100)])
memoryBlocks = [None] * 100

class FileSchema:

	backPointer = 0
	forwardPointer = 0
	userData = ""

	def __init__(self, backPointer = 0, forwardPointer = 0, userData = ""):
		self.backPointer = backPointer
		self.forwardPointer = forwardPointer
		self.userData = userData

class DirectorySchema:

	backPointer = 0
	forwardPointer = 0
	free = 0
	filler = 0
	directories = None

	def __init__(self):
		self.directories = [{
			"blockType": "F",
			"fileName": "",
			"link": 0,
			"size": 0
		} for _ in range(31)]

# file = FileSchema(100, 200, "hello")
# dirs = DirectorySchema()
# print(dirs.directories[0].blockType)

class FileSystem:
	root = DirectorySchema()
	memoryBlocks[0] = root

	def create(self, blockType, fileName):
		currentDir = self.root
		filePaths = fileName.split("/")
		for filePath in filePaths[1:-1]:
			for directory in currentDir.directories:
				if directory["fileName"] == filePath:
					currentDir = memoryBlocks[directory["link"]]
					break
		if blockType == "D":
			for directory in currentDir.directories:
				if directory["blockType"] == "F":
					# print(directory["link"], directory["blockType"], directory["fileName"], directory["size"])
					directory["blockType"] = "D"
					directory["fileName"] = filePaths[-1]
					self.root.free = freeBlockList.pop()
					directory["link"] = self.root.free
					memoryBlocks[self.root.free] = DirectorySchema()
					break
		if blockType == "U":
			for directory in currentDir.directories:
				if directory["blockType"] == "F":
					# print(directory["link"], directory["blockType"], directory["fileName"], directory["size"])
					directory["blockType"] = "U"
					directory["fileName"] = filePaths[-1]
					self.root.free = freeBlockList.pop()
					directory["link"] = self.root.free
					memoryBlocks[self.root.free] = FileSchema()
					break

fileSystem = FileSystem()
fileSystem.create("D", "root/dir1")
fileSystem.create("D", "root/dir1/dir2")
# print(memoryBlocks[1].directories[0]["fileName"])
fileSystem.create("D", "root/dir1/dir3")
fileSystem.create("U", "root/dir1/file1")
print(memoryBlocks[1].directories)
# print(memoryBlocks[0].directories)
print(memoryBlocks)