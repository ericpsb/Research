''' Given a binary string of the annotation, return a pair of lists, 
the first of which contains the size of strings of contiguous 0s,
and the second of which contains the sizes of strings of contiguous 1s'''
def rawAnn_to_lists(annotation):
  binStr = re.sub(r' ', '', annotation)
  binStr = binStr.encode()
  zeros = []  #array to hold strings with contiguous 0s
  ones  = []  #array to hold strings with contiguous 1s
  count = 1 #size of current contiguous str
  prevChar = binStr[0]
  for c in binStr[1: len(binStr)-1]: #for all but first char in annotation
    if c == prevChar:
      count = count+1 #add the char to the current str of same chars
    else:
      if c == '0': #previous str was 1s
        ones = ones + [count] #add the count to the ones list
      else: #previous str was 0s
        zeros = zeros + [count] #add the count to the zeros list
      prevChar = c
      count = 1
  return (zeros, ones)
    
''' get word count of binary string annotation '''
def bin_wordCount(annotation):
  return len(annotation.split())