library(lubridate)

#Dictionary for blogs
n.blogs <- 46
blogs <- c('ablogonthespectrum.blogspot.com', 'adiaryofamom.com', 'adventuresinautism.blogspot.co.uk', 'alyric.blogspot.com', 'aspergersquare8.blogspot.com', 
           'autism-vicky.blogspot.com', 'autism.typepad.com', 'autismandoughtisms.wordpress.com', 'autismblogsdirectory.blogspot.com', 'autismcrisis.blogspot.com:', #10
           'autismgadfly.blogspot.com', 'autisminnb.blogspot.com', 'autismjabberwocky.blogspot.com', 'autismnaturalvariation.blogspot.com', 'autismschmatism.blogspot.com', 
           'autismsedges.blogspot.com', 'autismsucksrocks.blogspot.com', 'bloom-parentingkidswithdisabilities.blogspot.com', 'carrielink.blogspot.com', 'chavisory.wordpress.com', #20
           'club166.blogspot.com', 'confessionsofanaspergersmom.blogspot.com', 'daysixtyseven.blogspot.com', 'donnathomson.com', 'elvis-sightings.blogspot.com:', 
           'embracingchaos.stephanieallencrist.com', 'esteeklar.com', 'extraordinary-ordinary.net', 'fullspectrummama.blogspot.com', 'hoopdeedoo.blogspot.com', #30
           'idoinautismland.com', 'injectingsense.blogspot.com', 'jennyalice.com', 'joeyandymom.blogspot.com', 'juststimming.wordpress.com', 
           'leftbrainrightbrain.co.uk', 'letitbeautism.blogspot.com', 'lizditz.typepad.com', 'lovethatmax.com', 'maternalinstincts.wordpress.com', #40
           'mfamama.typepad.com:my-blog', 'momnos.blogspot.com', 'motherofshrek.blogspot.com', 'noahsdad.com', 'onedadsopinion.blogspot.com', 
           'questioning-answers.blogspot.com', 'qw88nb88.wordpress.com', 'rebekahscot.wordpress.com', 'rhemashope.wordpress.com', 'roostercalls.blogspot.com', #50
           'specialed.wordpress.com', 'spectrumliving.blogspot.com', 'squashedmom.com', 'squidalicious.com', 'stimcity.org', 
           'stimeyland.com', 'susanetlinger.typepad.com', 'susansenator.com:blog', 'teenautism.com', 'theadventuresofboywonder.blogspot.com', #60
           'thefamilyvoyage.blogspot.com', 'therocchronicles.wordpress.com', 'thismom.blogs.com', 'tinygracenotes.blogspot.com', 'trydefyinggravity.wordpress.com:tag:autism', 
           'unstrangemind.com')
startDates <- as.Date(c('2006-05-07', '2008-03-30', '2004-07-19', '2005-03-01', '2016-06-03', 
                        '2008-10-05', '2005-06-17', '2010-10-30', '2016-06-03', '2016-06-03', #10
                        '2016-06-03', '2006-08-20', '2009-01-21', '2006-02-23', '2006-09-28', 
                        '2005-11-29', '2016-06-03', '2016-06-03', '2010-07-04', '2016-06-03', #20
                        '2007-01-26', '2009-07-13', '2005-10-03', '2016-06-03', '2008-07-08', 
                        '2009-07-05', '2008-10-05', '2016-06-03', '2012-01-11', '2007-01-17', #30
                        '2016-06-03', '2005-08-07', '2003-12-25', '2006-05-09', '2016-06-03', 
                        '2003-06-22', '2008-03-10', '2004-08-15', '2016-06-03', '2007-04-22', #40
                        '2016-06-03', '2005-02-09', '2007-08-19', '2016-06-03', '2007-04-08', 
                        '2016-06-03', '2007-04-22', '2009-11-25', '2008-05-02', '2008-02-20', #50
                        '2006-01-20', '2008-07-24', '2010-02-06', '2003-05-10', '2011-03-06', 
                        '2007-03-02', '2007-02-10', '2005-10-14', '2008-03-16', '2010-09-08', #60
                        '2006-01-16', '2008-09-17', '2005-01-30', '2016-06-03', '2010-01-17', 
                        '2016-06-03'))
# calling this "years" since we don't actually know birth date
birthYears <- as.Date(c('2001-07-02', '2006-07-02', '2002-07-02', NA, NA,
                        NA, '1997-07-02', '2006-07-02', NA, NA,
                        NA, '1995-07-02', '2005-07-02', NA, '2001-07-02',
                        '1997-07-02', NA, NA, '1996-07-02', NA, 
                        '2000-07-02', '1995-07-02', '2002-07-02', NA, '2004-07-02', 
                        '2000-07-02', '2002-07-02', NA, '2001-07-02', '2005-07-02', 
                        NA,'1999-07-02', '2000-07-02', '2003-07-02', NA, 
                        '2000-07-02', '1999-07-02', NA, NA, '2004-07-02', 
                        NA, '2000-07-02', '1988-07-02', NA, '2002-07-02', 
                        NA, NA, '2005-07-02', '2004-07-02', '2004-07-02', 
                        '2004-07-02', '2005-07-02', '2002-07-02', '2000-07-02', '2006-07-02', 
                        '2003-07-02', '2003-07-02', '1989-07-02', '1994-07-02', '2006-07-02', 
                        '2002-07-02', '2005-07-02', '2001-07-02', NA, '2006-07-02', 
                        NA))
# these are the blogs selected for inclusion in the corpus to be analyzed
indices <- c(1, 2, 3, 4, 7,
             8, 12, 13, 14, 15,
             16, 19, 21, 22, 23,
             25, 26, 27, 29, 30,
             32, 33, 34, 36, 37,
             40, 42, 43, 45, 48,
             49, 50, 51, 52, 53,
             54, 55, 56, 57, 58,
             59, 60, 61, 62, 63,
             65)

dataSetBegin <- as.Date('2003-05-22')
dataSetEnd <- as.Date('2016-06-03')

#Normalize dates
working <- docs.and.topics
working$date <- data$date

working$actualdate <- as.Date("1 January2", "%d%m%m")
working$dateTenureShift  <- as.Date("1 January2", "%d%m%m")
working$dateBirthShift <- as.Date("1 January2", "%d%m%m")

for (i in 1:nrow(working)){
  if (working$blogid[i] == 3 || working$blogid[i] == 8 || working$blogid[i] == 20 || working$blogid[i] == 26 || working$blogid[i] == 28 || working$blogid[i] == 31 || working$blogid[i] == 40 || working$blogid[i] == 41 || working$blogid[i] == 48 || working$blogid[i] == 49 || working$blogid[i] == 55 || working$blogid[i] == 56 || working$blogid[i] == 57 || working$blogid[i] == 59 || working$blogid[i] == 62 || working$blogid[i] == 63 || working$blogid[i] == 65){
    d <- as.Date(working$date[i], "%B %d, %Y")
  }
  else if (working$blogid[i] == 1 || working$blogid[i] == 4 || working$blogid[i] == 6 || working$blogid[i] == 11 || working$blogid[i] == 23 || working$blogid[i] == 18 || working$blogid[i] == 35){
    d <- as.Date(working$date[i], " %B %d, %Y")
  }
  else if (working$blogid[i] == 2|| working$blogid[i] == 27|| working$blogid[i] == 36|| working$blogid[i] == 51|| working$blogid[i] == 66){
    d <- as.Date(working$date[i], "%Y/%m/%d")
  }
  else if (working$blogid[i] == 7 || working$blogid[i] == 61){
    d <- as.Date(working$date[i], "%d %B %Y")
  }
  else if (working$blogid[i] == 33){
    d <- as.Date(working$date[i], "%d %B, %Y")
  }
  else if (working$blogid[i] == 47){
    d <- as.Date(working$date[i], " %d %B %Y")
  }
  else if (working$blogid[i] == 43 || working$blogid[i] == 46){
    d <- as.Date(working$date[i], "%A, %d %B %Y")
  }
  else if (working$blogid[i] == 44){
    d <- as.Date(working$date[i], ",%B,%d,%Y")
  }
  else if (working$blogid[i] == 54){
    d <- as.Date(working$date[i], "%m.%d.%Y")
  }
  else if (working$blogid[i] == 34){
    d <- as.Date(working$date[i], " %A, %B %d, %Y")
  }
  else{
    d <- as.Date(working$date[i], "%A, %B %d, %Y")
  }
  
  # epsb
  # figure out the offsets for this blog
  working$tenureOffset[i] <- startDates[as.numeric(working$blogid[i])] - dataSetBegin
  working$birthOffset[i] <- birthYears[as.numeric(working$blogid[i])] - dataSetBegin
  working$actualdate[i] <- d
}

#Make a new table and aggregate weekly averages

sub.working <- subset(working, blogid %in% indices)
sub.working$month <- as.Date(cut(sub.working$actualdate,breaks = "month"))
sub.working$month <- month(sub.working$actualdate)
sub.working$week <- as.Date(cut(sub.working$actualdate, breaks = "week", start.on.monday = FALSE))
sub.working$monthTenureShift <- sub.working$month - sub.working$tenureOffset
sub.working$weekTenureShift <- sub.working$week - sub.working$tenureOffset
sub.working$weekTenureShift <- as.Date(cut(sub.working$weekTenureShift, breaks = "week", start.on.monday = FALSE))
sub.working$monthBirthShift <- sub.working$month - sub.working$birthOffset
sub.working$weekBirthShift <- sub.working$week - sub.working$birthOffset
sub.working$weekBirthShift <- as.Date(cut(sub.working$weekBirthShift, breaks = "week", start.on.monday = FALSE))

df <- sub.working
df$link <- NULL
df$title <- NULL
df$text <- NULL
df$date <- NULL
df$actualdate <- NULL
df$month <- NULL
df$dateTenureShift <- NULL
df$monthTenureShift <- NULL
df$dateBirthShift <- NULL
df$monthBirthShift <- NULL
df$blogid <- as.numeric(df$blogid)
df$week <- as.Date(df$actualdate)
df$year <- format(df$week, "%Y")
df$year <- as.numeric(df$year)
df$tenureOffset <- NULL
df$birthOffset <- NULL
df$weekTenureShift <- NULL
df$weekBirthShift <- NULL
df$posts <- df$blogid

df2 <- df
df2 <- df2[, -c(2:52)]

# Replace underscores in column names with commas and spaces


# ag will provide week-by-week aggregates (for temporal visualization)
# agTotal will provide overall aggregates (for cosine visualization)
attach(df)
ag <- aggregate(df, by=list(df$blogid, df$week), FUN = mean)
agTotal <- aggregate(df, by=list(df$blogid), FUN = mean)
agYearly <- aggregate(df, by = list(df$blogid, df$year), FUN = mean)
agTotalPosts <- aggregate(df2, by=list(df2$blogid), FUN = sum)
agYearlyPosts <- aggregate(df2, by = list(df2$blogid, df2$year), FUN = sum)
detach(df)

ag$Group.1 <- NULL
ag$Group.2 <- NULL
ag$year <- NULL
ag$posts <- NULL

agTotal$Group.1 <- NULL
agTotal$week <- NULL
agTotal$year <- NULL
agTotal$tenureOffset <- NULL
agTotal$birthOffset <- NULL
agTotal$posts <- NULL

agTotalPosts$blogid <- agTotalPosts$Group.1
agTotalPosts$Group.1 <- NULL
agTotalPosts$year <- NULL
agTotalPosts$posts <- agTotalPosts$posts / agTotalPosts$blogid
totalposts <- agTotalPosts

agYearly$week <- NULL
agYearly$year <- agYearly$Group.2
agYearly$Group.1 <- NULL
agYearly$Group.2 <- NULL
agYearly$posts <- NULL

agYearlyPosts$blogid <- agYearlyPosts$Group.1
agYearlyPosts$Group.1 <- NULL
agYearlyPosts$year <- agYearlyPosts$Group.2
agYearlyPosts$Group.2 <- NULL
agYearlyPosts$posts <- agYearlyPosts$posts / agYearlyPosts$blogid

agYearly <- merge(x = agYearly, y = agYearlyPosts, by = c("blogid", "year"))
agYearly$Group.1 <- NULL
agYearly$Group.2 <- NULL

file.remove("ag.csv")
file.remove("agTotal.csv")
file.remove("agYearly.csv")
write.csv(ag, file = "ag.csv",row.names=FALSE)
write.csv(agTotal, file = "agTotal.csv", row.names=FALSE)
write.csv(agYearly, file = "agYearly.csv", row.names=FALSE)

file.remove("yearlydata.js")
file.create("yearlydata.js")
tojs <- "var yearlydata = ["
write(x = tojs, file = "yearlydata.js", append = TRUE)
for (i in c(1:length(agYearly[,1]))) {
  tojs <- ""
  tojs <- paste(tojs, "[", sep = " ")
  for (j in c(1: length(agYearly[i,]))) {
    tojs <- paste(tojs, agYearly[i, j], sep = " ")
    if (j < length(agYearly[i,])) {
      tojs <- paste(tojs, ",", sep = "")
    }
  }
  tojs <- paste(tojs, "]", sep = "")
  if (i < length(agYearly[,1])) {
    tojs <- paste(tojs, ",", sep = "")
  }
  write(x = tojs, file = "yearlydata.js", append = TRUE)
}
tojs <- "]"
write(x = tojs, file = "yearlydata.js", append = TRUE)

file.remove("totalposts.js")
file.create("totalposts.js")
tojs <- "var totalposts = ["
write(x = tojs, file = "totalposts.js", append = TRUE)
for (i in c(1:length(totalposts[,1]))) {
  tojs <- ""
  tojs <- paste(tojs, "[", sep = " ")
  for (j in c(1: length(totalposts[i,]))) {
    tojs <- paste(tojs, totalposts[i, j], sep = " ")
    if (j < length(totalposts[i,])) {
      tojs <- paste(tojs, ",", sep = "")
    }
  }
  tojs <- paste(tojs, "]", sep = "")
  if (i < length(totalposts[,1])) {
    tojs <- paste(tojs, ",", sep = "")
  }
  write(x = tojs, file = "totalposts.js", append = TRUE)
}
tojs <- "]"
write(x = tojs, file = "totalposts.js", append = TRUE)

# Make stacked line plots
#library(xts)
#DF <- subset(ag, blogid == 34)
#dfxts <- xts(DF[,-1], order.by=DF$week)
#dfxts$week <- NULL

#DF<-dfxts
#matplot(DF[,-1], col=1:ncol(DF), type='l', lty=1,  axes=FALSE)

#plot.xts(dfxts, screens = factor(1, 1), auto.legend = TRUE)

#library(ggplot2)
#DF <- subset(ag, blogid = 35)
#ggplot(df, aes(x = week, y = a, fill = c)) + geom_area(position = 'stack')


