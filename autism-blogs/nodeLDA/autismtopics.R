#Import necessary libraries
library(dplyr)
library (rJava)
.jinit()
.jinit(parameters="-Xmx12g") #Give rJava enough memory
library(mallet)
library(ggplot2)
library(reshape2)
library(jsonlite)


#Set number of topics
n.topics <- 50
long.label.length = 10

#Set working directory
setwd("C:/Users/a/Desktop/research17/das-lab/autism-blogs/nodeLDA")


#Import Json file to a data variable (requires formatting data once imported)
json_file <- "filtered_merged_file.json"
data <- fromJSON(json_file)
data <- bind_rows(data, .id = 'blog')


#Use rbind to create a documents variable from the data.frame
documents <- rbind(data.frame(blogid=data$blog, link=data$link, title=data$title, text=data$body,  stringsAsFactors=F))

#Use mallet as in sample code
mallet.instances <- mallet.import(documents$title, documents$text, "blog.stop", token.regexp = "\\p{L}[\\p{L}\\p{P}]+\\p{L}")

## Create a topic trainer object.
topic.model <- MalletLDA(num.topics=n.topics)

## Load our documents. We could also pass in the filename of a 
##  saved instance list file that we build from the command-line tools.
topic.model$loadDocuments(mallet.instances)

## Get the vocabulary, and some statistics about word frequencies.
#vocabulary <- topic.model$getVocabulary()
#word.freqs <- mallet.word.freqs(topic.model)

## Optimize hyperparameters every 20 iterations, 
##  after 50 burn-in iterations.
topic.model$setAlphaOptimization(20, 50)

## Now train a model.
##  We can specify the number of iterations. Here we'll use a large-ish round number.
topic.model$train(1000)
topic.model$maximize(50)

doc.topics <- mallet.doc.topics(topic.model, smoothed=T, normalized=T)
topic.words <- mallet.topic.words(topic.model, smoothed=T, normalized=T)
mallet.top.words(topic.model, topic.words[1,], 30)

#topics.labels <- gsub("\\W", "_", mallet.topic.labels(topic.model, topic.words, 3))
#topics.long.labels <- mallet.topic.labels(topic.model, topic.words, num.top.words=50)
topics.long.labels <- vector(length=n.topics)
for (topic.i in 1:n.topics) 
{
  topics.long.labels[topic.i] <- gsub(",", ";", paste(as.vector(mallet.top.words(topic.model, topic.words[topic.i,], long.label.length)[,1]), collapse="_"))
  topics.long.labels[topic.i] <- gsub("\\s", "_", topics.long.labels[topic.i])
}

doc.topics.frame <- data.frame(doc.topics)
#names(doc.topics.frame) <- paste("Topic", 1:n.topics, sep="")
names(doc.topics.frame) <- topics.long.labels
docs.and.topics <- cbind(documents, doc.topics.frame)

csv<-file("topic_frame.csv", encoding="UTF-8")
write.csv(doc.topics.frame, file=csv, quote=FALSE)
