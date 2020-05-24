n.classes = 5

# Joint Probability: mat[i, j] = p(i, j)
set.seed(0)
joint_probs = matrix(runif(n.classes^2), nrow=n.classes)
diag(joint_probs) <- 0
joint_probs[lower.tri(joint_probs)] = t(joint_probs)[lower.tri(joint_probs)]

joint_probs <- joint_probs / sum(joint_probs)
sum(joint_probs)

all(t(joint_probs) == joint_probs)

# Marginal from Joint
marginal_probs = colSums(joint_probs)

# Conditional Matrix: mat[i, j] = p(i|j) = p(i, j) / p(j)
cond_probs = matrix(numeric(n.classes^2), nrow=n.classes)
for (i in 1:n.classes) {
  for (j in 1:n.classes) {
    cond_probs[i, j] = joint_probs[i, j] / marginal_probs[j]
  }
}
rm(list=c('i', 'j'))

# Algorithm to sample pairs of 3
N = 1000
library(gtools)

combinations = t(permutations(n=n.classes, r=3, v=1:n.classes, repeats.allowed = F))
# combinations = combn(1:n.classes, 3)

generated = numeric(n.classes)
out_mat = matrix(numeric(1), nrow=length(combinations), ncol=n.classes)

tot_1 = 0
tot_2 = 0
tot_3 = 0
tot_all = 0

for (i in 1:ncol(combinations)) {
  print(i)
  comb_i1 = combinations[1, i]
  comb_i2 = combinations[2, i]
  comb_i3 = combinations[3, i]

  marg_i1 = marginal_probs[comb_i1]
  cond_i21 = cond_probs[comb_i2, comb_i1]
  cond_i31 = cond_probs[comb_i3, comb_i1]
  joint_123 = cond_i21 * cond_i31 * marg_i1
  # tot_1 = tot_1 + joint_123 * factorial(3)
  tot_1 = tot_1 + joint_123

  new_rows = (N * joint_123)

  if (new_rows > 0) {
      new_vec = numeric(n.classes)
      new_vec[c(comb_i1, comb_i2, comb_i3)] = new_rows
      out_mat[i, ] = new_vec
  }

  generated[comb_i1] = generated[comb_i1] + new_rows
  generated[comb_i2] = generated[comb_i2] + new_rows
  generated[comb_i3] = generated[comb_i3] + new_rows

  # print(paste(new_rows, sum(out_mat), sum(generated)))

  # marg_i2 = marginal_probs[comb_i2]
  # cond_i12 = cond_probs[comb_i1, comb_i2]
  # cond_i32 = cond_probs[comb_i3, comb_i2]
  # tot_2 = tot_2 + cond_i12 * cond_i32 * marg_i2 * factorial(3)
  # 
  # marg_i3 = marginal_probs[comb_i3]
  # cond_i13 = cond_probs[comb_i1, comb_i3]
  # cond_i23 = cond_probs[comb_i2, comb_i3]
  # tot_3 = tot_3 + cond_i13 * cond_i23 * marg_i3 * factorial(3)

  # print(paste(comb_i1, comb_i2, comb_i3))
  # print(paste(cond_i21 * cond_i31 * marg_i1, cond_i12 * cond_i32 * marg_i2, cond_i13 * cond_i23 * marg_i3))
}
tot_all = tot_1 + tot_2 + tot_3
rm(list=c('i', 'comb_i1', 'comb_i2', 'comb_i3', 'marg_i1', 'marg_i2', 'marg_i3',
          'cond_i12', 'cond_i13', 'cond_i21', 'cond_i23', 'cond_i31', 'cond_i32'))

generated
colSums(out_mat)
empirical_marginal = generated / sum(generated)


# Check Marginal Distribution
sum((empirical_marginal - marginal_probs)^2)

# Check Joint Distribution
empirical_joint = matrix(numeric(1), nrow=n.classes, ncol=n.classes)
for (i in 1:n.classes) {
  for (j in 1:n.classes) {
    if (i != j) {
      rows = out_mat[which(out_mat[, j] >= 1 & out_mat[, i] >= 1), ]
      empirical_joint[i, j] = sum(rows)
    }
  }
}

empirical_joint = empirical_joint / sum(empirical_joint)

# Check Conditional Distributions
# mat[i, j] = p(i|j) = p(i, j) / p(j)
empirical_cond = matrix(numeric(1), nrow=n.classes, ncol=n.classes)
for (i in 1:n.classes) {
  for (j in 1:n.classes) {
    if (i != j) {
      empirical_cond[i, j] = empirical_joint[i, j] / empirical_marginal[j]
    }
  }
}
empirical_cond

## Sanity Checks
# Joint and Marginals all work out
combinations = combn(1:n.classes, 2)
tot_ij = 0
for (k in 1:ncol(combinations)) {
  comb_k = combinations[, k]
  i = comb_k[1]
  j = comb_k[2]
  
  cond_ij = cond_probs[i, j]
  marg_i = marginal_probs[i]
  joint_ij = joint_probs[i, j]
  cond_ji = cond_probs[j, i]
  marg_j = marginal_probs[j]

  # print(paste(i, j, '| Cond(ij) * marg(j)', cond_ij * marg_j))
  # print(paste(i, j, '| Cond(ji) * marg(i)', cond_ji * marg_i))
  # stopifnot(cond_ij * marg_j == cond_ji * marg_i)
  # stopifnot(cond_ij * marg_j == joint_ij)
  tot_ij = tot_ij + cond_ij * marg_j
}
rm(list=c('i', 'j', 'k', 'comb_k', 'cond_ij', 'cond_ji', 'marg_i', 'marg_j', 'joint_ij'))


