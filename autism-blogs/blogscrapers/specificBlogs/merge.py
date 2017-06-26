import json
import glob

def merge():
  result = []
  for f in glob.glob("Done/*/linksb.json"):
      with open(f, "rb") as infile:
        result.append(json.load(infile))

  with open("merged_file.json", "wb") as outfile:
     json.dump(result, outfile)

if __name__ == '__main__':
	merge()