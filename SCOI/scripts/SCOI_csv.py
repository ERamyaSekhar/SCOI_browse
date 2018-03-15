import csv

class SCOI(object):
    def main(self):
        with open(self.filename, 'w+') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(self.fields)


