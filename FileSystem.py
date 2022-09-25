freeBlockList = set([i for i in range(1, 100)])
memoryBlocks = [None] * 100

class FileSchema:

	backPointer = 0
	forwardPointer = 0
	userData = ""

	def __init__(self, backPointer, forwardPointer, userData):
		self.backPointer = backPointer
		self.forwardPointer = forwardPointer
		self.userData = userData

class BlockSchema:

	blockType = "F"
	fileName = ""
	link = 0
	size = 0

class DirectorySchema:

	backPointer = 0
	forwardPointer = 0
	free = 1
	filler = 0
	directories = [BlockSchema() for _ in range(31)]

# file = FileSchema(100, 200, "hello")
# dirs = DirectorySchema()
# print(dirs.directories[0].blockType)

class FileSystem:
	root = DirectorySchema()
	memoryBlocks[0] = root

	def create(self, blockType, fileName):
		if blockType == "D":
			currentDir = self.root
			filePaths = fileName.split("/")
			for filePath in filePaths[1:-1]:
				for directory in currentDir.directories:
					if directory.fileName == filePath:
						currentDir = memoryBlocks[directory.link]
						break
			for directory in currentDir.directories:
				if directory.blockType == "F":
					directory.blockType = "D"
					directory.fileName = filePaths[-1]
					print(filePaths[-1])
					directory.link = self.root.free
					memoryBlocks[self.root.free] = DirectorySchema()
					self.root.free = freeBlockList.pop()
					break

fileSystem = FileSystem()
# print(memoryBlocks)
print(freeBlockList)
fileSystem.create("D", "root/dir1")
# print(memoryBlocks[0].directories[0].fileName)
fileSystem.create("D", "root/dir1/dir2")
print(memoryBlocks)