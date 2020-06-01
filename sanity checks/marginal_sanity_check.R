#!/usr/bin/env Rscript
setwd("~/Documents/projects/poke2vec/")
source("sanity checks/helpers.R")

#### Prepare Data ####
filename = "data/txt/teams_2019-06_gen7ou_1695.txt"
temp <- generate.team.encode(filename)
team_encode <- temp$teams
poke_names <- temp$pokemon
counts <- temp$counts

filename = "data/txt/mprob_2019-06_gen7ou_1695.txt"
true_marginal = read.csv(filename, stringsAsFactors = F)

rm(temp, filename)


marginal_probs <- colSums(team_encode) / sum(counts)

# marginal_probs[which(poke_names %in% c("Clefable", "Excadrill", "Dragapult"))]
# marginal_probs[which(poke_names %in% c("Mew", "Hydreigon", "Crawdaunt"))]
# marginal_probs[which(poke_names %in% c("Indeedee", "Mamoswine", "Lapras"))]
# names(sort(marginal_probs, decreasing = T))

suppressMessages(library(dplyr))

joined.data <- as_tibble(marginal_probs) %>%
  mutate(pokemon=names(marginal_probs), value=value/6) %>%
  rename(est.prob=value) %>% select(pokemon, est.prob) %>%
  right_join(as_tibble(true_marginal), by=c('pokemon'='pokemon')) %>%
  mutate(est.prob = ifelse(is.na(est.prob), 0, est.prob)) %>%
  mutate(prob.delta = true.prob - est.prob) %>%
  arrange(desc(true.prob))


set.seed(0)
rand.dist <- runif(nrow(joined.data))
rand.dist <- rand.dist / sum(rand.dist)

c(KL.obs=KL.DIVERGENCE(joined.data$true.prob, joined.data$est.prob),
  KL.rand=KL.DIVERGENCE(joined.data$true.prob, rand.dist))

