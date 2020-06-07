generate.team.encode <- function(filename) {
  data = read.csv(filename, header=F, stringsAsFactors = F)
  teams = data[, 1:6]
  counts = data[, 7]
  poke_names <- as.character(unique(unlist(teams)))
  
  teams_encode = matrix(0, nrow=nrow(teams), ncol=length(poke_names))
  colnames(teams_encode) <- poke_names
  for (i in 1:nrow(teams)) {
    new_vec <- numeric(length(poke_names))
    for (j in 1:ncol(teams)) {
      new_vec[which(poke_names == teams[i, j])] = counts[i]
    }
    teams_encode[i, ] = new_vec
  }
  
  return(list(teams=teams_encode,
              pokemon=poke_names,
              counts=counts))
}

KL.DIVERGENCE <- function(p, q, p2=p, fix.val=1e-10) {
  p[which(p == 0)] = fix.val
  q[which(q == 0)] = fix.val
  sum(p2 * log(p / q))
}

compute_true_joint <- function(true_conditional, true_marginal) {
  temp <- as_tibble(true_conditional) %>%
    left_join(as_tibble(true_marginal),
              by=c('cond.pokemon'='pokemon'),
              suffix=c(".cond", ".marg")) %>%
    mutate(true.prob.joint=true.prob.cond * true.prob.marg) %>%
    select(base.pokemon, cond.pokemon, true.prob.joint)

  temp
}