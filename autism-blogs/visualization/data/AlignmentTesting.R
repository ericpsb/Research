# @author: epsb
# Collection of methods to test the various date-shift-based alignments.

require(psych)
require(reshape2)
require(ggplot2)
require(colorspace)

n.blogs <- 44 # not 100% sure why we lose one...
dataSetBegin <- as.Date('2003-05-22')
dataSetEnd <- as.Date('2016-06-03')

intrp <- read.csv("interpolated.csv")
intrp$Date <- as.Date(intrp$Date)
intrp$TenureShift <- as.Date(intrp$TenureShift)

# find the quartile size of the date range
date.quart <- (max(intrp$Date) - min(intrp$Date)) * 0.25

# convert blogs to factors
intrp$BlogID <- factor(intrp$BlogIndex)
subi <- subset(intrp, 
               Date > min(Date) + date.quart & Date < max(Date) - date.quart)

# show where we actually have interpolated data
# subset(intrp,
#        Date > min(Date) + date.quart & 
#          Date < max(Date) - date.quart), 
myplot <- ggplot(subi, aes(x=Date, y=BlogID)) + 
  geom_point(aes(color=(InterpolationLevel == 0)), 
             shape=I('l'), size=3) + 
  guides(colour = guide_legend(title = "Data for Each Week"))
myplot

# plotting to make sure the tenure shift is correct
myplot <- ggplot(intrp, aes(x=TenureShift, y=BlogID)) + 
  geom_point(aes(color=(InterpolationLevel == 0)), 
             shape=I('l'), size=3) + 
  guides(colour = guide_legend(title = "Data for Each Week")) +
  xlim(dataSetBegin, dataSetEnd)
myplot

# plotting to make sure the birth shift is correct
myplot <- ggplot(intrp, aes(x=BirthShift, y=BlogID)) + 
  geom_point(aes(color=(InterpolationLevel == 0)), 
             shape=I('l'), size=3) + 
  guides(colour = guide_legend(title = "Data for Each Week"))
  # + xlim(dataSetBegin, dataSetEnd)
myplot

# project topic scores into colors
hcl.palette <- rainbow_hcl(50) # this is our number of topics
palette.R <- lapply(hcl.palette, function(x) strtoi(substr(x, 2, 3), base=16))
palette.G <- lapply(hcl.palette, function(x) strtoi(substr(x, 4, 5), base=16))
palette.B <- lapply(hcl.palette, function(x) strtoi(substr(x, 6, 7), base=16))

topics.proprtions <- intrp[, grep("Topic", colnames(intrp)) ]
intrp[925:935, grep("Topic", colnames(intrp)) ] * palette.R

# check topic alignment over time
topic.num = 8 # which topic are we comparing?
topic.name <- sprintf("Topic%02d", topic.num)

foo <- intrp[c("BlogIndex", "Date", topic.name)]
unShifted <- dcast(foo, Date ~ BlogIndex, value.var = topic.name)
foo <- intrp[c("BlogIndex", "TenureShift", topic.name)]
tenureShifted <- dcast(foo, TenureShift ~ BlogIndex, value.var = topic.name)
tenureShifted <- subset(tenureShifted, TenureShift > dataSetBegin)
foo <- intrp[c("BlogIndex", "BirthShift", topic.name)]
birthShifted <- dcast(foo, BirthShift ~ BlogIndex, value.var = topic.name, 
                      fun.aggregate = sum)
#birthShifted <- subset(birthShifted, birthShift > dataSetBegin)

# calculate ICCs on this topic for each time shift 
ICC(unShifted[2:45], missing = FALSE)
ICC(tenureShifted[2:45], missing = FALSE)
ICC(birthShifted[2:45], missing = FALSE)

