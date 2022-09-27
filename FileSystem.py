freeBlockList = set([i for i in range(1, 100)])
memoryBlocks = [None] * 100

class FileSchema:

	backPointer = 0
	forwardPointer = 0
	userData = ""

	def __init__(self, backPointer = 0):
		self.backPointer = backPointer

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

class FileSystem:
	root = DirectorySchema()
	memoryBlocks[0] = root
	openedFile = None

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

	def delete(self, fileName):
		currentDir = self.root
		fileLink = -1
		filePaths = fileName.split("/")
		for filePath in filePaths[1:-1]:
			for directory in currentDir.directories:
				if directory["fileName"] == filePath:
					currentDir = memoryBlocks[directory["link"]]
					break
		for directory in currentDir.directories:
			if directory["blockType"] == "U" and directory["fileName"] == filePaths[-1]:
				fileLink = directory["link"]
				directory["blockType"] = "F"
				directory["fileName"] = ""
				directory["link"] = 0
				break

		while fileLink:
			freeBlockList.add(fileLink)
			newFileLink = memoryBlocks[fileLink].forwardPointer
			memoryBlocks[fileLink] = None
			fileLink = newFileLink
			

	def open(self, mode, fileName):
		if self.openedFile:
			print("Another file is already open. Please close that file to open new file")
			return

		currentDir = self.root
		filePaths = fileName.split("/")
		for filePath in filePaths[1:-1]:
			for directory in currentDir.directories:
				if directory["fileName"] == filePath:
					currentDir = memoryBlocks[directory["link"]]
					break
		for directory in currentDir.directories:
			if directory["blockType"] == "U" and directory["fileName"] == filePaths[-1]:
				self.openedFile = {
					"mode": mode,
					"name": fileName,
					"link": directory["link"]
					# "link": memoryBlocks[directory["link"]]
				}
				break

	def close(self):
		if self.openedFile:
			self.openedFile = None

	def read(self, n):
		fileLink = self.openedFile["link"]
		howManyFilesRead = 0
		i = 0
		while howManyFilesRead * 256 + i < n:
			if i == 256:
				if memoryBlocks[fileLink].forwardPointer:
					fileLink = memoryBlocks[fileLink].forwardPointer
					howManyFilesRead += 1
					i = 0
				else: 
					print("EOF")
					return
			else:
				if i == len(memoryBlocks[fileLink].userData): 
					print("EOF")
					return 
				print(memoryBlocks[fileLink].userData[i], end="")
				i += 1
		print()

	def write(self, n, data):
		fileLink = self.openedFile["link"]
		if len(data) < n:
			data = data + " " * (n - len(data))
		else:
			data = data[:n]

		i = 0
		while i < n:
			if len(memoryBlocks[fileLink].userData) == 256:
				self.root.free = freeBlockList.pop()
				memoryBlocks[fileLink].forwardPointer = self.root.free
				memoryBlocks[self.root.free] = FileSchema(fileLink)
				fileLink = self.root.free
				continue
			memoryBlocks[fileLink].userData += data[i]
			i += 1
		# memoryBlocks[self.openedFile["link"]].userData = data

fileSystem = FileSystem()
fileSystem.create("D", "root/dir1")
fileSystem.create("D", "root/dir1/dir2")
# print(memoryBlocks[1].directories[0]["fileName"])
fileSystem.create("D", "root/dir1/dir3")
fileSystem.create("U", "root/dir1/file1")
# print(memoryBlocks[1].directories)
# print(memoryBlocks[0].directories)
print(memoryBlocks)
print(fileSystem.openedFile)
fileSystem.open("I", "root/dir1/file1")
print(fileSystem.openedFile)
fileSystem.write(600, "1" * 700)
# print(memoryBlocks[4].userData)
# print(memoryBlocks[5].userData)
# print(memoryBlocks[6].userData)
fileSystem.read(601)
fileSystem.close()
print(fileSystem.openedFile)
print(memoryBlocks)

fileSystem.delete("root/dir1/file1")
print(memoryBlocks)
print(freeBlockList)









