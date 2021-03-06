#Auxillary Code
n.blogs <- 64
result = c()
for (i in 1:(n.blogs)){
  sub.data <- subset(docs.and.topics, blogid==i)
  for (k in 5:(n.topics + 4)){
    result <- c(result, mean(sub.data[,k]))
  }
}

write(result,"mydata.txt")
sub.data <- subset(working, blogid==1)

#get Representative rows
counter <- 1
dates = c()
for (i in 1:42341){
  if (working$blogid[i] == counter){
    counter <- counter +1
    dates[working$blogid[i]] <- working$actualdate[i]
  }
}
write(dates, "repdates.txt")

#Normalize dates
working <- docs.and.topics
working$date <- data$date
working$actualdate <- as.Date("1 January2", "%d%m%m")

for (i in 1:42341){
  if (working$blogid[i] == 1 || working$blogid[i] == 4 || working$blogid[i] == 6 || working$blogid[i] == 11|| working$blogid[i] == 17){
    d <- as.Date(working$date[i], " %b %d, %Y")
  }
  if (working$blogid[i] == 2|| working$blogid[i] == 26|| working$blogid[i] == 35|| working$blogid[i] == 50|| working$blogid[i] == 64){
    d <- as.Date(working$date[i], "%Y/%m/%d")
  }
  if (working$blogid[i] == 3 || working$blogid[i] == 8|| working$blogid[i] == 19|| working$blogid[i] == 22|| working$blogid[i] == 25|| working$blogid[i] == 27|| working$blogid[i] == 30|| working$blogid[i] == 34|| working$blogid[i] == 39|| working$blogid[i] == 40|| working$blogid[i] == 47|| working$blogid[i] == 48|| working$blogid[i] == 55|| working$blogid[i] == 56|| working$blogid[i] == 58|| working$blogid[i] == 61|| working$blogid[i] == 63){
    d <- as.Date(working$date[i], "%b %d, %Y")
  }
  if (working$blogid[i] == 5 || working$blogid[i] == 9 || working$blogid[i] == 10 || working$blogid[i] == 12|| working$blogid[i] == 13|| working$blogid[i] == 14|| working$blogid[i] == 15|| working$blogid[i] == 16|| working$blogid[i] == 18|| working$blogid[i] == 20|| working$blogid[i] == 21|| working$blogid[i] == 24|| working$blogid[i] == 28|| working$blogid[i] == 29|| working$blogid[i] == 31|| working$blogid[i] == 33|| working$blogid[i] == 36|| working$blogid[i] == 37|| working$blogid[i] == 38|| working$blogid[i] == 41|| working$blogid[i] == 44|| working$blogid[i] == 49|| working$blogid[i] == 51|| working$blogid[i] == 52|| working$blogid[i] == 57|| working$blogid[i] == 59|| working$blogid[i] == 62){
    d <- as.Date(working$date[i], "%A, %B %d, %Y")
  }
  if (working$blogid[i] == 7){
    d <- as.Date(working$date[i], "%d %B %Y")
  }
  if (working$blogid[i] == 23){
    d <- as.Date("1 January2", "%d%m%m")
  }
  if (working$blogid[i] == 32){
    d <- as.Date(working$date[i], "%d %B, %Y")
  }
  if (working$blogid[i] == 42){
    d <- as.Date(working$date[i], "%A, %d %B %Y")
  }
  if (working$blogid[i] == 43){
    d <- as.Date(working$date[i], ",%B,%d,%Y")
  }
  if (working$blogid[i] == 45){
    d <- as.Date(working$date[i], "%A, %d %B %Y")
  }
  if (working$blogid[i] == 46){
    d <- as.Date(working$date[i], "\n\t\t\t\t%d %B %Y")
  }
  if (working$blogid[i] == 53){
    d <- as.Date(working$date[i], "%m.%B.%Y")
  }
  if (working$blogid[i] == 60){
    d <- as.Date(working$date[i], "%d %b %Y")
  }
  working$actualdate[i] <- d
  
}
library(xts)
apply.monthly(x.zoo, mean) 

ggplot(data = sub.data,
  aes(Month, Quantity)) +
  stat_summary(fun.y = sum, # adds up all observations for the month
               geom = "bar") + # or "line"
  scale_x_date(
    labels = date_format("%Y-%m"),
    breaks = "1 month") # custom x-axis labels


library(lubridate)
sub.data$my <- floor_date(sub.data$Date, "month")

# topics =c("vaccine_vaccines_thimerosal", "school_day_kids", "little_christmas_photo", "science_vaccines_david", "wakefield_mmr_paper",
#          "school_students_education", "study_children_data", "words_language_word", "research_iacc_health", "care_family_home",
#          "disorder_spectrum_disorders", "mercury_treatment_chelation", "back_bike_car", "use_ipad_computer", "drug_states_health", 
#          "blog_post_read", "know_see_girl", "car_water_trip", "know_time_get", "hair_wear_wearing", "beauty_thomas_children",
#          "child_children_parents", "food_eat_eating", "conference_blogher_san", "music_show_song", "case_court_law", "time_get_know",
#          "help_skills_therapy", "people_disability_disabilities", "joy_dog_snow", "thank_love_words", "children_aba_treatment",      
#          "mom_day_friends", "money_job_pay", "people_person_different", "see_research_paper", "kids_special_needs", 
#          "neurodiversity_speaks_cure", "government_canada_children", "life_love_day", "back_got_told", "down_syndrome_baby", "today_big_got",
#          "brain_genetic_research", "post_link_name", "book_read_story", "night_sleep_bed", "police_story_mother", "doctor_hospital_pain",
#          "little_down_head")
# epsb
# make the generation of topic labels respond to the outputs of topic modeling rather than hard-coded
topics = names(docs.and.topics[(length(names(docs.and.topics))-50 + 1):length(names(docs.and.topics))])

library(plyr)
data.set <- data.frame(date, topic, averageproportion)
for (i in 1:(n.topics)){
  
}

ne <- ddply(sub.data, "my", summarise, x = mean(night_sleep_bed))

ggplot(ne, aes(my, x)) + geom_line() + xlab("") + ylab("vaccine_vaccines_thimerosal") + stat_smooth()

data.set <- data.frame(
  Time = c(rep(1, 4),rep(2, 4), rep(3, 4), rep(4, 4)),
  Type = rep(c('a', 'b', 'c', 'd'), 4),
  Value = rpois(16, 10)
)

qplot(Time, Value, data = data.set, fill = Type, geom = "area")

#Dictionary for blogs
blogs <- c('ablogonthespectrum.blogspot.com', 'adiaryofamom.com', 'adventuresinautism.blogspot.co.uk', 'alyric.blogspot.com', 'aspergersquare8.blogspot.com', 'autism-vicky.blogspot.com', 'autism.typepad.com', 'autismandoughtisms.wordpress.com', 'autismblogsdirectory.blogspot.com', 'autismcrisis.blogspot.com:', 'autismgadfly.blogspot.com', 'autisminnb.blogspot.com', 'autismjabberwocky.blogspot.com', 'autismnaturalvariation.blogspot.com', 'autismschmatism.blogspot.com', 'autismsucksrocks.blogspot.com', 'bloom-parentingkidswithdisabilities.blogspot.com', 'carrielink.blogspot.com', 'chavisory.wordpress.com', 'club166.blogspot.com', 'confessionsofanaspergersmom.blogspot.com', 'daysixtyseven.blogspot.com', 'donnathomson.com', 'elvis-sightings.blogspot.com:', 'embracingchaos.stephanieallencrist.com', 'esteeklar.com', 'extraordinary-ordinary.net', 'fullspectrummama.blogspot.com', 'hoopdeedoo.blogspot.com', 'idoinautismland.com', 'injectingsense.blogspot.com', 'jennyalice.com', 'joeyandymom.blogspot.com', 'juststimming.wordpress.com', 'leftbrainrightbrain.co.uk', 'letitbeautism.blogspot.com', 'lizditz.typepad.com', 'lovethatmax.com', 'maternalinstincts.wordpress.com', 'mfamama.typepad.com:my-blog', 'momnos.blogspot.com', 'motherofshrek.blogspot.com', 'noahsdad.com', 'onedadsopinion.blogspot.com', 'questioning-answers.blogspot.com', 'qw88nb88.wordpress.com', 'rebekahscot.wordpress.com', 'rhemashope.wordpress.com', 'roostercalls.blogspot.com', 'specialed.wordpress.com', 'spectrumliving.blogspot.com', 'squashedmom.com', 'squidalicious.com', 'stimcity.org', 'stimeyland.com', 'susanetlinger.typepad.com', 'susansenator.com:blog', 'teenautism.com', 'theadventuresofboywonder.blogspot.com', 'thefamilyvoyage.blogspot.com', 'therocchronicles.wordpress.com', 'tinygracenotes.blogspot.com', 'trydefyinggravity.wordpress.com:tag:autism', 'unstrangemind.wordpress.com')

library(jsonlite)
x <- toJSON(docs.and.topics)
write(x, "mydata.json")


mylist <- head(unique[order(-unique$V1),], 739)
mylist <- data.frame(lapply(mylist, as.character), stringsAsFactors=FALSE)
for (i in 1:739){
  write(mylist[i,]$V2, file = "stop.txt", append = TRUE, sep = " \n")
  #print (mylist[i,]$V2)
}


#Print the top 30 words for each of the topics into an outfile.txt
for (i in 1:(n.topics)){
  mylist = (mallet.top.words(topic.model, topic.words[i,], 30))
  lapply(mylist, write, "outfile2.txt", append=TRUE, ncolumns=1000)
}


#Sort docs.and.topics by a category 
head(docs.and.topics[order(-docs.and.topics$autism_this_some),], 10)

#Print top ten representative documents to reps.txt
for (i in 5:(n.topics + 4)){
  header <- paste("\n\n\n\n\n\n\nTopic Name: ", colnames(docs.and.topics)[i], "\n\n\n\n\n\n\n\n\n\n\n\n\n\n", sep = "")
  write(header, "reps.txt", append = TRUE)
  write.table(head(docs.and.topics[order(-docs.and.topics[,i]),], 20), "reps.txt", append = TRUE)
}



#corrgram of specific blog to topics
library(corrgram)
copy <- docs.and.topics
copy$title = NULL
copy$text = NULL
copy$blogid = NULL
copy$link  = NULL
corr <- corrgram(copy)





#Heatmap of Blog vs. mean log topic proportions
library(data.table)  # faster fread() and better weekdays()
library(dplyr)       # consistent data.frame operations
library(tidyr)       # consistent data.frame cleaning
library(lubridate)   # date manipulation
library(ggplot2)     # base plots are for Coursera professors
library(scales)      # pairs nicely with ggplot2 for plot label formatting
library(gridExtra)   # a helper for arranging individual ggplot objects
library(ggthemes)    # has a clean theme for ggplot2
library(viridis)     # best. color. palette. evar.
library(knitr)       # kable : prettier data.frame output

#Get the log proportions
copy <- docs.and.topics
copy$title = NULL
copy$text = NULL
copy$link = NULL
copy[1:1] <- sapply(copy[1:1], as.numeric)
copy[, 2:(n.topics+1)] <- log(copy[2:(n.topics+1)])

#change name of column with duplicate name
#colnames(copy)[7] <- "not_about_all2"

#Aggegate and format date
copa <- aggregate(.~blogid, data=copy, mean) #can change to median
copa.m <- melt(copa, id=c("blogid"))

#Rescale data between 0 and 1 
copa.m$rescale = (copa.m$value - min(copa.m$value))/diff(range(copa.m$value))

#Create and format ggplot
gg <- ggplot(copa.m, aes(x=variable, y=blogs[blogid], fill=rescale))
gg <- gg + geom_tile(color="white", size=0.1)
gg <- gg + scale_fill_viridis(name="# log poportion", label=comma)
gg <- gg + coord_equal()
gg <- gg + labs(x=NULL, y=NULL, title="Mean Log Topic Proportion Per Blog")
gg <- gg + theme_tufte(base_family="Helvetica")
gg <- gg + theme(plot.title=element_text(hjust=0))
gg <- gg + theme(axis.ticks=element_blank())
gg <- gg + theme(axis.text=element_text(size=6))
gg <- gg + theme(legend.title=element_text(size=8))
gg <- gg + theme(legend.text=element_text(size=6))
gg <- gg + theme(axis.text.x  = element_text(angle=90, vjust=0.5))
#gg <- gg + theme(axis.text.y  = element_text(angle=90, vjust=0.5, size = 16))

#Display Heatmap
print(gg)



#Clustering Code
library(ggdendro)
topic.sim = matrix(nrow = n.topics, ncol = n.topics)
for (i in 1:(n.topics))
{
  for (j in 1:(n.topics))
  {
    topic.sim[i,j] = 1.0 - length(intersect(topics.long.labels[i], topics.long.labels[j])) / length(union(topics.long.labels[i], topics.long.labels[j]))
    if (topic.sim[i,j] > 0 & topic.sim[i,j] < 1)
    {
      print(topic.sim[i,j])
    }
  }
}
names(topic.sim) <- topics.labels
rownames(topic.sim) <- topics.labels


hcl <- hclust(as.dist(topic.sim))
dendr <- dendro_data(hcl, type="rectangle")
ggplot() +
  geom_segment(data=segment(dendr), aes(x=x, y=y, xend=xend, yend=yend)) +
  geom_text(data=label(dendr), aes(x=x, y=y, label=label, hjust=0), size=1) +
  coord_flip() + scale_y_reverse(expand=c(1.0, 0)) +
  theme(axis.line.y=element_blank(),
        axis.ticks.y=element_blank(),
        axis.text.y=element_blank(),
        axis.title.y=element_blank(),
        panel.background=element_rect(fill="white"),
        panel.grid=element_blank())


#Tokenizing script
library(NLP)
library(jsonlite)
json_file <- "merged_file.json"
data <- fromJSON(json_file)
data <- bind_rows(data, .id = 'blog')


#Word Graphs
hist(work$V2, breaks = seq(0, 3000, by=250), xlab = "# of Posts", main = "Frequency of number of posts")









#CLUSTER CODE
n.topics <- 50 # this might need to be, and probably should be, adjusted based on the total number of questions whose responses are being included as documents
num_long_words = 25 # the number of words to use for "long" topic labels
num.runs = 10 # number of total topic model solution runs

mallet.instances <- mallet.import(documents$title, documents$text, "blog.stop", token.regexp = "\\p{L}[\\p{L}\\p{P}]+\\p{L}")

all.topics <- matrix(nrow = n.topics * num.runs, ncol = num_long_words)
all.topic.labels <- character(n.topics * num.runs)

for (run_num in 0:(num.runs - 1))
{
  
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
  doc.topics <- 0.1 * mallet.doc.topics(topic.model, smoothed=T, normalized=T)
  topic.words <- 0.1 * mallet.topic.words(topic.model, smoothed=T, normalized=T)
  
  for (sample.iter in 1:9) {
    topic.model$train(100)
    doc.topics <- doc.topics + 0.1 * mallet.doc.topics(topic.model, smoothed=T, normalized=T)
    topic.words <- topic.words + 0.1 * mallet.topic.words(topic.model, smoothed=T, normalized=T)
  }
  
  #topic.model$maximize(50)
  
  #doc.topics <- mallet.doc.topics(topic.model, smoothed=T, normalized=T)
  #topic.words <- mallet.topic.words(topic.model, smoothed=T, normalized=T)
  # mallet.top.words(topic.model, topic.words[1,], 25)
  
  #topics.labels <- gsub("\\W", "_", mallet.topic.labels(topic.model, topic.words, 5))
  topics.labels <- vector(length=n.topics)
  for (topic.i in 1:n.topics) 
  {
    topics.labels[topic.i] <- gsub("\\W", "_", paste(as.vector(mallet.top.words(topic.model, topic.words[topic.i,], 5)[,1]), collapse="_"))
  }
  #topics.long.labels <- mallet.topic.labels(topic.model, topic.words, num.top.words=50)
  topics.long.labels <- vector(length=n.topics)
  for (topic.i in 1:n.topics)
  {
    topics.long.labels[topic.i] <- paste(as.vector(mallet.top.words(topic.model, topic.words[topic.i,], 25)[,1]), collapse = " ")
  }
  
  #library("sets") # NB: masks %>% from dplyr
  
  topic.sets <- matrix(nrow=n.topics, ncol=num_long_words)
  for (topic.i in 1:n.topics)
  {
    topic.sets[topic.i,] <- as.vector(mallet.top.words(topic.model, topic.words[topic.i,], 25)[,1])
  }
  
  
  doc.topics.frame <- data.frame(doc.topics)
  #names(doc.topics.frame) <- paste("Topic", 1:n.topics, sep="")
  names(doc.topics.frame) <- topics.labels
  docs.and.topics <- cbind(documents, doc.topics.frame)

  mask = topics.labels
  melted.docs.and.topics <- melt(docs.and.topics, id.vars=c("blogid", "link", "title", "text"), variable.name="topic")
  wide.data <- dcast(melted.docs.and.topics %>% group_by(blogid, text, topic) %>% summarise(value = mean(log(value))), id + text ~ topic, FUN=mean)
  wide.data[,4:28] <- wide.data[,4:28] - (rowSums(wide.data[,4:28]) / n.topics)
  formula.string <- paste(names(wide.data)[4:28][mask], collapse=" + ")
  user.topics <- as.matrix(wide.data[,4:28])

  
  summary(glm(paste("return", " ~ ", formula.string), data=wide.data, family=binomial()))
  
  for (i in 1:n.topics)
  {
    all.topics[i + n.topics * run_num,] <- topic.sets[i,]
  }
  
  all.topic.labels[(1 + n.topics * run_num):(n.topics + n.topics * run_num)] <- topics.labels[1:25]
  
 }# end for (run_num in 0:(num.runs - 1))

rownames(all.topics) <- all.topic.labels

topic.sim = matrix(nrow = n.topics * num.runs, ncol = n.topics * num.runs)
for (i in 1:(n.topics * num.runs))
{
  for (j in 1:(n.topics * num.runs))
  {
    topic.sim[i,j] = 1 - length(intersect(all.topics[i,], all.topics[j,])) / length(union(all.topics[i,], all.topics[j,]))
  }
}
#names(topic.sim) <- all.topic.labels
names(topic.sim) <- paste(all.topic.labels, as.character(rep(c(1:10), each=25)), as.character(rep(c(1:25), 10)), sep=" - ")
#rownames(topic.sim) <- all.topic.labels
rownames(topic.sim) <- paste(all.topic.labels, as.character(rep(c(1:10), each=25)), as.character(rep(c(1:25), 10)), sep=" - ")

# the following is if we are only analyzing similarity for one run
topic.sim = matrix(nrow = n.topics, ncol = n.topics)
for (i in 1:(n.topics))
{
  for (j in 1:(n.topics))
  {
    topic.sim[i,j] = 1.0 - length(intersect(topics.long.labels[i], topics.long.labels[j])) / length(union(topics.long.labels[i], topics.long.labels[j]))
    if (topic.sim[i,j] > 0 & topic.sim[i,j] < 1)
    {
      print(topic.sim[i,j])
    }
  }
}
names(topic.sim) <- topics.labels
rownames(topic.sim) <- topics.labels

require(ggdendro)
require(ggplot2)

hcl <- hclust(as.dist(topic.sim))
dendr <- dendro_data(hcl, type="rectangle") 
ggplot() + 
  geom_segment(data=segment(dendr), aes(x=x, y=y, xend=xend, yend=yend)) + 
  geom_text(data=label(dendr), aes(x=x, y=y, label=label, hjust=0), size=1) +
  coord_flip() + scale_y_reverse(expand=c(1.0, 0)) + 
  theme(axis.line.y=element_blank(),
        axis.ticks.y=element_blank(),
        axis.text.y=element_blank(),
        axis.title.y=element_blank(),
        panel.background=element_rect(fill="white"),
        panel.grid=element_blank())




hcl <- hclust(dist(t(user.topics)))
dendr <- dendro_data(hcl, type="rectangle") 

ggplot() + 
  geom_segment(data=segment(dendr), aes(x=x, y=y, xend=xend, yend=yend)) + 
  geom_text(data=label(dendr), aes(x=x, y=y, label=label, hjust=0), size=5) +
  coord_flip() + scale_y_reverse(expand=c(1.0, 0)) + 
  theme(axis.line.y=element_blank(),
        axis.ticks.y=element_blank(),
        axis.text.y=element_blank(),
        axis.title.y=element_blank(),
        panel.background=element_rect(fill="white"),
        panel.grid=element_blank())





