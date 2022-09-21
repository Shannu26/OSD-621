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

root = DirectorySchema()
memoryBlocks[0] = root