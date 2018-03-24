install.packages("RMySQL")
library(RMySQL)

db = dbConnect(MySQL(), user = 'root', password = 'nasdaq93', dbname = 'hedge_fund',
               host = '127.0.0.1')

dbListTables(db)

install.packages("dplyr")
install.packages("magrittr")
install.packages("ggplot2")

library(dplyr)
library(magrittr)
library(ggplot2)


bloom <- dbSendQuery(db, "select * from eurusd where source = 'bloomberg'")

data <- fetch(bloom, n = -1)
mind <- min(data$datetime)
maxd <- max(data$datetime)

query <- paste0("select * from eurusd where source = 'histdata' and datetime between '", as.character(mind),
       "' and '", as.character(maxd), "'")

histdata <- dbSendQuery(db, query)
histdata <- fetch(histdata, n = -1)
