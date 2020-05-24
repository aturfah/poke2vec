set.seed(10)
n.classes = 66

## Helpers
KL.DIVERGENCE <- function(p, q, fix.val=1e-10) {
  p[which(p == 0)] = fix.val
  q[which(q == 0)] = fix.val
  sum(p * log(p / q))
}

#### TRUE DISTRTIBUTIONS ####

# Generate Data with 3-D Joint Structure
true.joint = array(numeric(1), dim=rep(n.classes, 3))
for (i in 1:n.classes) {
  for (j in i:n.classes) {
    if (i == j) {
      next
    }
    for (k in j:n.classes) {
      if (k == i || k == j) {
        next
      }
      true.joint[i, j, k] = rpois(1, n.classes) / i
      true.joint[i, k, j] = true.joint[i, j, k]
      true.joint[j, i, k] = true.joint[i, j, k]
      true.joint[j, k, i] = true.joint[i, j, k]
      true.joint[k, j, i] = true.joint[i, j, k]
      true.joint[k, i, j] = true.joint[i, j, k]
    }
  }
}
true.joint = true.joint / sum(true.joint)

rm(list=c('i', 'j', 'k'))

# 2-D Joint Distribution
true.joint.2D = apply(true.joint, 1, colSums)
stopifnot(all(true.joint.2D == apply(true.joint, 2, colSums)))
stopifnot(all(true.joint.2D == apply(true.joint, 3, colSums)))

# Marginal Distribution
true.marginal = apply(true.joint, 1, sum)

# 3-D Conditional Distribution
# Conditional Matrix: mat[i, j, k] = p(i, j|k) = p(i, j, k) / p(k)
true.conditional.1 = array(numeric(1), dim=rep(n.classes, 3))
true.conditional.2 = array(numeric(1), dim=rep(n.classes, 3))
true.conditional.3 = array(numeric(1), dim=rep(n.classes, 3))
for (i in 1:n.classes) {
  for (j in i:n.classes) {
    if (i == j) {
      next
    }
    for (k in j:n.classes) {
      if (k == i || k == j) {
        next
      }
      true.conditional.3[i, j, k] = true.joint[i, j, k] / true.marginal[k]
      true.conditional.3[i, k, j] = true.joint[i, k, j] / true.marginal[j]
      true.conditional.3[j, i, k] = true.joint[j, i, k] / true.marginal[k]
      true.conditional.3[j, k, i] = true.joint[j, k, i] / true.marginal[i]
      true.conditional.3[k, j, i] = true.joint[k, j, i] / true.marginal[i]
      true.conditional.3[k, i, j] = true.joint[k, i, j] / true.marginal[j]
      
      true.conditional.2[i, j, k] = true.joint[i, j, k] / true.marginal[j]
      true.conditional.2[i, k, j] = true.joint[i, k, j] / true.marginal[k]
      true.conditional.2[j, i, k] = true.joint[j, i, k] / true.marginal[i]
      true.conditional.2[j, k, i] = true.joint[j, k, i] / true.marginal[k]
      true.conditional.2[k, j, i] = true.joint[k, j, i] / true.marginal[j]
      true.conditional.2[k, i, j] = true.joint[k, i, j] / true.marginal[i]
      
      true.conditional.1[i, j, k] = true.joint[i, j, k] / true.marginal[i]
      true.conditional.1[i, k, j] = true.joint[i, k, j] / true.marginal[i]
      true.conditional.1[j, i, k] = true.joint[j, i, k] / true.marginal[j]
      true.conditional.1[j, k, i] = true.joint[j, k, i] / true.marginal[j]
      true.conditional.1[k, j, i] = true.joint[k, j, i] / true.marginal[k]
      true.conditional.1[k, i, j] = true.joint[k, i, j] / true.marginal[k]
    }
  }
}
rm(list=c('i', 'j', 'k'))


stopifnot(sum(apply(true.conditional.1, 1, sum)) == n.classes)
stopifnot(sum(apply(true.conditional.2, 2, sum)) == n.classes)
stopifnot(sum(apply(true.conditional.3, 3, sum)) == n.classes)

# 2-D Conditional Distribution
# Conditional Matrix: mat[i, j] = p(i|j) = p(i, j) / p(j)
true.conditional.2D = apply(true.conditional.1, 1, colSums)
stopifnot(all(true.conditional.2D == apply(true.conditional.2, 2, colSums)))
stopifnot(all(true.conditional.2D == apply(true.conditional.3, 3, colSums)))


#### SAMPLING THE TRUE DISTRIBUTIONS ####
library(gtools)

# possibilities = t(permutations(n=n.classes, r=3, v=1:n.classes, repeats.allowed = F))
possibilities = combn(1:n.classes, 3)
sampled.results = matrix(numeric(1), nrow=ncol(possibilities), ncol=n.classes)

for (i in 1:ncol(possibilities)) {
  comb_i1 = possibilities[1, i]
  comb_i2 = possibilities[2, i]
  comb_i3 = possibilities[3, i]

  joint_123 = true.conditional.2D[comb_i1, comb_i3] * true.conditional.2D[comb_i2, comb_i3] * true.marginal[comb_i3] +
    true.conditional.2D[comb_i1, comb_i2] * true.conditional.2D[comb_i3, comb_i2] * true.marginal[comb_i2] +
    true.conditional.2D[comb_i3, comb_i1] * true.conditional.2D[comb_i2, comb_i1] * true.marginal[comb_i1]
  joint_123 = joint_123 / 3
  
  # Instead of actually generating a sample, why not work with the probabilities directly
  # Use this value as a weight, using a one-hot encoding
  sampled.results[i, c(comb_i1, comb_i2, comb_i3)] = joint_123
}
rm(list=c('i','comb_i1', 'comb_i2', 'comb_i3', 'joint_123'))

# Empirical Marginal
empirical.marginal = colSums(sampled.results) / sum(sampled.results)

# Empirical 2-D Joint
empirical.joint.2D = matrix(numeric(1), nrow=n.classes, ncol=n.classes)
for (i in 1:n.classes) {
  for (j in 1:n.classes) {
    if (i == j) {
      next
    }
    empirical.joint.2D[i, j] = sum(sampled.results[which(sampled.results[, i] > 0 & sampled.results[, j] > 0), ])
  }
}
empirical.joint.2D = empirical.joint.2D / sum(empirical.joint.2D)
rm(list=c('i', 'j'))


# Empirical 2-D Conditional
empirical.conditional.2D = matrix(numeric(1), nrow=n.classes, ncol=n.classes)
for (i in 1:n.classes) {
  for (j in 1:n.classes) {
    if (i == j) {
      next
    }
    empirical.conditional.2D[i, j] = empirical.joint.2D[i, j] / empirical.marginal[j]
  }
}
rm(list=c('i', 'j'))


#### Evaluation ####
c(
  marginal=KL.DIVERGENCE(true.marginal, empirical.marginal),
  joint=KL.DIVERGENCE(true.joint.2D, empirical.joint.2D),
  conditional=KL.DIVERGENCE(true.conditional.2D, empirical.conditional.2D)
)