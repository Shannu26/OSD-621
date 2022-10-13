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

	def __init__(self, backPointer = 0):
		self.directories = [{
			"blockType": "F",
			"fileName": "",
			"link": 0,
			"size": 0
		} for _ in range(31)]
		self.backPointer = backPointer

class FileSystem:
	root = DirectorySchema()
	memoryBlocks[0] = root
	openedFile = None

	def create(self, blockType, fileName):
		currentDir = self.root
		dirLink = 0
		filePaths = fileName.split("/")
		for filePath in filePaths[1:-1]:
			currentDir = memoryBlocks[self.findDirectory(currentDir, filePath)]

		self.extendIfExtensionRequired(dirLink)
		isFreeAvailable = False

		while not isFreeAvailable:
			for directory in currentDir.directories:
				if directory["blockType"] == "F":
					isFreeAvailable = True
					break
			if not isFreeAvailable:
				currentDir = memoryBlocks[currentDir.forwardPointer]

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

	def findDirectory(self, currentDir, dirName):
		currDir = currentDir

		while True:
			for directory in currDir.directories:
				if directory["blockType"] == "D" and directory["fileName"] == dirName:
					return directory["link"]
			currDir = memoryBlocks[currDir.forwardPointer]

	def extendIfExtensionRequired(self, memoryLink):
		dirLink = memoryLink
		isAvailable = False
		while not isAvailable:
			for directory in memoryBlocks[dirLink].directories:
				if directory["blockType"] == "F": 
					isAvailable = True
					break

			if not isAvailable:
				if memoryBlocks[dirLink].forwardPointer:
					dirLink = memoryBlocks[dirLink].forwardPointer
				else:
					self.root.free = freeBlockList.pop()
					memoryBlocks[dirLink].forwardPointer = self.root.free
					memoryBlocks[self.root.free] = DirectorySchema(dirLink)
					isAvailable = True

	def delete(self, fileName):
		currentDir = self.root
		fileLink = -1
		filePaths = fileName.split("/")
		for filePath in filePaths[1:-1]:
			currentDir = memoryBlocks[self.findDirectory(currentDir, filePath)]

		fileFound = False

		while not fileFound:
			for directory in currentDir.directories:
				if directory["blockType"] == "U" and directory["fileName"] == filePaths[-1]:
					fileLink = directory["link"]
					directory["blockType"] = "F"
					directory["fileName"] = ""
					directory["link"] = 0
					fileFound = True
					break

			if not fileFound:
				if currentDir.forwardPointer == 0: 
					print("File Not Found Error")
					return
				currentDir = memoryBlocks[currentDir.forwardPointer]

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
			currentDir = memoryBlocks[self.findDirectory(currentDir, filePath)]

		while not self.openedFile:
			for directory in currentDir.directories:
				if directory["blockType"] == "U" and directory["fileName"] == filePaths[-1]:
					self.openedFile = {
						"mode": mode,
						"name": fileName,
						"link": directory["link"]
						# "link": memoryBlocks[directory["link"]]
					}
					return

			if not currentDir.forwardPointer: 
				print("File Not Found Error")
				return
			currentDir = memoryBlocks[currentDir.forwardPointer]

	def close(self):
		if self.openedFile:
			self.openedFile = None

	def read(self, n):
		fileLink = self.openedFile["link"]
		howManyFilesRead = 0
		i = 0
		while howManyFilesRead * 504 + i < n:
			if i == 504:
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
			if len(memoryBlocks[fileLink].userData) == 504:
				self.root.free = freeBlockList.pop()
				memoryBlocks[fileLink].forwardPointer = self.root.free
				memoryBlocks[self.root.free] = FileSchema(fileLink)
				fileLink = self.root.free
				continue
			memoryBlocks[fileLink].userData += data[i]
			i += 1
		# memoryBlocks[self.openedFile["link"]].userData = data


def main():
	fileSystem = FileSystem()
	# for i in range(72):
	# 	fileSystem.create("D", "root/dir" + str(i))
	# # print(memoryBlocks)
	# # print(fileSystem.root.forwardPointer)
	# # print(memoryBlocks[0].forwardPointer)
	# # print(memoryBlocks[fileSystem.root.forwardPointer].forwardPointer)

	# fileSystem.create("U", "root/file1")
	# print(fileSystem.openedFile)
	# fileSystem.open("I", "root/file1")
	# print(fileSystem.openedFile)
	# fileSystem.write(2000, "0" * 1010)
	# fileSystem.read(1000)
	# fileSystem.close()
	# fileSystem.create("U", "root/dir1/file1")
	# print(memoryBlocks)
	# fileSystem.delete("root/file1")
	# print(memoryBlocks)

	commands = []

	print("How do you want to Boot your System?")
	print("1. Launch new system")
	print("2. Restore from old save")
	bootOption = int(input("Enter your option: "))
	print(bootOption)
	if bootOption == 1: commands = []
	else: commands = []

	option = 1
	while option != 7:
		print("Which Operation do you want to implement?")
		print("1. Create")
		print("2. Delete")
		print("3. Open")
		print("4. Close")
		print("5. Read")
		print("6. Write")
		print("7. Shutdown")
		option = int(input("Enter your option: "))

		if option == 1:
			print("What do you want to Create?")
			print("1. Directory")
			print("2. File")
			blockType = int(input("Enter your option: "))
			if blockType == 1:
				fileName = input("Enter directory name: ")
				fileSystem.create("D", fileName)
			else:
				fileName = input("Enter file name: ")
				fileSystem.create("U", fileName)
		if option == 2:
			fileName = input("Enter file name to delete: ")
			fileSystem.delete(fileName)
		if option == 3:
			fileName = input("Enter file name to open: ")
			print("How do you want open the file?")
			print("I. Input Mode")
			print("O. Output Mode")
			print("U. Update Mode")
			mode = input("Enter your option: ")
			fileSystem.open(mode, fileName)

		print(memoryBlocks)


if __name__ == "__main__":
	main()










# fileSystem.create("D", "root/dir1")
# fileSystem.create("D", "root/dir1/dir2")
# # print(memoryBlocks[1].directories[0]["fileName"])
# fileSystem.create("D", "root/dir1/dir3")
# fileSystem.create("U", "root/dir1/file1")
# # print(memoryBlocks[1].directories)
# # print(memoryBlocks[0].directories)
# print(memoryBlocks)
# print(fileSystem.openedFile)
# fileSystem.open("I", "root/dir1/file1")
# print(fileSystem.openedFile)
# fileSystem.write(600, "1" * 700)
# # print(memoryBlocks[4].userData)
# # print(memoryBlocks[5].userData)
# # print(memoryBlocks[6].userData)
# fileSystem.read(601)
# fileSystem.close()
# print(fileSystem.openedFile)
# print(memoryBlocks)

# fileSystem.delete("root/dir1/file1")
# print(memoryBlocks)
# print(freeBlockList)









