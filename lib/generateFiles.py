import sys, string, random

#root = "/apps/pds/tools/ColumboNCCS/testfiles1/"
root = "/home/ib/dads/dan/progProj/pds-nccs/bulletins/tata/"
numFiles = sys.argv[1]
size = sys.argv[2]
letters = list(string.letters)
priority = range(1,6)

for num in range(int(numFiles)):
   output = open(root + "testfile" + str(num) + "_" + str(random.choice(priority)), 'w')
   randomString = "".join(map(lambda x: random.choice(letters), range(0, int(size))))
   output.write(randomString)
   output.close()

root = "/home/ib/dads/dan/progProj/pds-nccs/bulletins/titi/"
for num in range(int(numFiles)):
   output = open(root + "testfile" + str(num) + "_" + str(random.choice(priority)), 'w')
   randomString = "".join(map(lambda x: random.choice(letters), range(0, int(size))))
   output.write(randomString)
   output.close()

root = "/home/ib/dads/dan/progProj/pds-nccs/bulletins/toto/"
for num in range(int(numFiles)):
   output = open(root + "testfile" + str(num) + "_" + str(random.choice(priority)), 'w')
   randomString = "".join(map(lambda x: random.choice(letters), range(0, int(size))))
   output.write(randomString)
   output.close()
