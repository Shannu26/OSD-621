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
			if currentDir.forwardPointer == 0: raise Exception(dirName + " not found")
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
					raise Exception("File Not Found Error")
				currentDir = memoryBlocks[currentDir.forwardPointer]

		while fileLink:
			freeBlockList.add(fileLink)
			newFileLink = memoryBlocks[fileLink].forwardPointer
			memoryBlocks[fileLink] = None
			fileLink = newFileLink
			

	def open(self, mode, fileName):

		self.openedFile = None
		currentDir = self.root
		filePaths = fileName.split("/")
		for filePath in filePaths[1:-1]:
			currentDir = memoryBlocks[self.findDirectory(currentDir, filePath)]

		while not self.openedFile:
			for directory in currentDir.directories:
				if directory["blockType"] == "U" and directory["fileName"] == filePaths[-1]:
					print(directory["size"])
					self.openedFile = {
						"mode": mode,
						"name": fileName,
						"link": directory["link"],
						"dir": directory,
					}
					return

			if not currentDir.forwardPointer: 
				raise Exception("File Not Found Error")
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
		j = 0
		while i < n:
			if j == 504:
				if memoryBlocks[fileLink].forwardPointer:
					fileLink = memoryBlocks[fileLink].forwardPointer
				else:
					self.root.free = freeBlockList.pop()
					memoryBlocks[fileLink].forwardPointer = self.root.free
					memoryBlocks[self.root.free] = FileSchema(fileLink)
					fileLink = self.root.free
				j = 0
				continue
			memoryBlocks[fileLink].userData = memoryBlocks[fileLink].userData[:j] + data[i] + memoryBlocks[fileLink].userData[j + 1:]
			i += 1
			j += 1
		if memoryBlocks[fileLink].forwardPointer == 0: self.openedFile["dir"]["size"] = len(memoryBlocks[fileLink].userData)

def restoreOS(fileSystem):
	commands = []
	with open("OS_Status.txt", "r") as reader:
		commands = list(reader.readlines())
		print(commands)
		for command in commands:
			parts = command.split(" ")
			if parts[0] == "CREATE":
				fileSystem.create(parts[1], parts[2][:-1])
			if parts[0] == "DELETE":
				fileSystem.delete(parts[1][:-1])
			if parts[0] == "OPEN":
				fileSystem.open(parts[1], parts[2][:-1])
			if parts[0] == "CLOSE":
				fileSystem.close()
			if parts[0] == "WRITE":
				fileSystem.write(int(parts[1]), " ".join(parts[2:-1]) + " " + parts[-1][:-1])
	print(memoryBlocks)
	return commands

def saveOS(commands):
	with open("OS_Status.txt", "w") as writer:
		writer.writelines(commands)

def main():
	fileSystem = FileSystem()

	commands = []

	print("How do you want to Boot your System?")
	print("1. Launch new system")
	print("2. Restore from old save")
	bootOption = int(input("Enter your option: "))
	if bootOption == 2: commands = restoreOS(fileSystem)
	if bootOption == 1: commands = []
	# print(commands)

	option = 1
	while option != 7:
		try:
			print("Which Operation do you want to implement?")
			print("1. Create")
			print("2. Delete")
			print("3. Open")
			print("4. Close")
			print("5. Read")
			print("6. Write")
			print("7. Shutdown")
			option = int(input("Enter your option: "))
			command = ""
			if option == 1:
				command = "CREATE "
				print("What do you want to Create?")
				print("1. Directory")
				print("2. File")
				blockType = int(input("Enter your option: "))
				if blockType == 1:
					command += "D "
					fileName = input("Enter directory name: ")
					command += fileName
					fileSystem.create("D", fileName)
				else:
					command += "U "
					fileName = input("Enter file name: ")
					command += fileName
					fileSystem.create("U", fileName)
				commands.append(command + "\n")
			if option == 2:
				fileName = input("Enter file name to delete: ")
				command = "DELETE " + fileName
				commands.append(command + "\n")
				fileSystem.delete(fileName)
			if option == 3:
				fileName = input("Enter file name to open: ")
				print("How do you want open the file?")
				print("I. Input Mode")
				print("O. Output Mode")
				print("U. Update Mode")
				mode = input("Enter your option: ")
				command = "OPEN " + mode + " " + fileName
				commands.append(command + "\n")
				fileSystem.open(mode, fileName)
			if option == 4:
				fileSystem.close()
				commands.append("CLOSE\n")
			if option == 5:
				n = int(input("Enter number of bytes you want to read: "))
				fileSystem.read(n)
			if option == 6:
				text = input("Enter the data you want to enter: ")
				n = int(input("Enter number of bytes you want to enter: "))
				fileSystem.write(n, text)
				command = "WRITE " + str(n) + " " + text
				print(command)
				commands.append(command + "\n")
			if option == 7:
				saveOS(commands)

		except Exception as error:
			print(error)

		print(memoryBlocks)
		print(fileSystem.openedFile)

if __name__ == "__main__":
	main()

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

