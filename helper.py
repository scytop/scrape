FILE_NAME = "records.txt"

def getInstructors(fileName = FILE_NAME):
  iFile = open("instructors.txt", 'w+')
  f = open(fileName, 'r')
  f.readline()
  for line in f:
    info = line.split('\t')
    if(len(info) == 6):
      instructors = info[-1]
    else:
      continue
    instructor = instructors.split('/')
    for i in instructor:
      iFile.write(i.strip())
      iFile.write('\n')
  f.close()
  iFile.close()



#def saveInstructors(instructorList):



