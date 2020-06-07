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

filename = "data/txt/mprob_2019-06_gen7ou_1695.txt"
true_marginal = read.csv(filename, stringsAsFactors = F)

rm(temp, filename)

#### Calculate true joint distribution ####
true_joint <- compute_true_joint(true_conditional, true_marginal)

#### Iterate through teams, calculating conditional probability ####
temp_joint <- mclapply(poke_names, function (cond_name) {
  ## Get in form Cond | Base
  output <- list()
  cond_idx <- which(poke_names == cond_name)
  n_total <- sum(counts)

  for (base_name in poke_names) {
    if (cond_name == base_name) next
    base_idx <- which(poke_names == base_name)
    n_joint_rows <- as_tibble(team_encode) %>%
      filter(!!as.name(cond_name) > 0 & !!as.name(base_name) > 0) %>%
      summarise(n=sum(!!as.name(base_name))) %>% pull()

    print(paste(cond_name, "|", base_name, "|", n_joint_rows, "/", n_total))
    output[[base_name]] <- c(n_joint_rows / n_total, n_joint_rows)
  }
  output
}, mc.cores=ceiling(detectCores() / 1.5))
names(temp_joint)  <- poke_names


emp_joint <- data.frame(poke1=c("temp"), poke2=c("temp"), est.count=c(-1), est.prob=c(-1))
for (poke1 in names(temp_joint)) {
  for (poke2 in names(temp_joint[[poke1]])) {
    prob <- temp_joint[[poke1]][[poke2]][1]
    count <- temp_joint[[poke1]][[poke2]][2]
    emp_joint <- add_row(emp_joint, poke1=poke1, poke2=poke2, est.count=count, est.prob=prob)
  }
}
rm(poke2, poke1, prob)
emp_joint <- emp_joint %>% filter(est.prob >= 0)

sum(emp_joint$est.prob)
sum(emp_joint$est.count)