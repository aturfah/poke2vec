#!/usr/bin/env Rscript
setwd("~/Documents/projects/poke2vec/")
source("sanity checks/helpers.R")

suppressMessages(library(parallel))
suppressMessages(library(dplyr))


#### Prepare Data ####
filename = "data/txt/teams_2019-06_gen7ou_1695.txt"
temp <- generate.team.encode(filename)
team_encode <- temp$teams
poke_names <- temp$pokemon
counts <- temp$counts

filename = "data/txt/cprob_2019-06_gen7ou_1695.txt"
true_conditional = read.csv(filename, stringsAsFactors = F)


#### Iterate through teams, calculating conditional probability ####
inv.cond <- mclapply(poke_names, function (cond_name) {
  ## Get in form Cond | Base
  output <- list()
  cond_idx <- which(poke_names == cond_name)
  cond_rows <- as_tibble(team_encode) %>%
    filter(!!as.name(cond_name) > 0)
  n_cond <- cond_rows %>% select(matches(cond_name)) %>% summarise(n=sum(!!as.name(cond_name))) %>% pull()  
  
  for (base_name in poke_names) {
    if (cond_name == base_name) next
    base_idx <- which(poke_names == base_name)
    n_base_cond <- cond_rows %>% select(matches(base_name)) %>% summarise(n=sum(!!as.name(base_name))) %>% pull()
    output[[base_name]] <- n_base_cond / n_cond
  }
  output
}, mc.cores=floor(detectCores() / 2))

names(inv.cond) <- poke_names
# inv.cond

gen_conditional <- data.frame(base.poke=c("temp"), cond.poke=c("temp"), est.prob=c(-1))
for (cond_name in names(inv.cond)) {
  for (base_name in names(inv.cond[[cond_name]])) {
    prob <- inv.cond[[cond_name]][[base_name]]
    # print(paste(base_name, "|", cond_name, "|", prob))
    gen_conditional <- add_row(gen_conditional, base.poke=base_name, cond.poke=cond_name, est.prob=prob)
  }
}

rm(base_name, cond_name, prob)
gen_conditional <- gen_conditional %>% filter(est.prob >= 0)

#### Join Conditional Distributions and Compare ####
joined_data <- gen_conditional %>%
  left_join(true_conditional, by=c("base.poke"="base.pokemon", "cond.poke"="cond.pokemon"))

set.seed(0)
rand.dist <- runif(nrow(joined_data))
rand.dist <- rand.dist / sum(rand.dist)


## TODO: KL For Conditional is https://math.stackexchange.com/a/3678282
c(KL.obs=KL.DIVERGENCE(joined_data$true.prob, joined_data$est.prob),
  KL.rand=KL.DIVERGENCE(joined_data$true.prob, rand.dist))

