#!/usr/bin/env Rscript
setwd("~/Documents/projects/poke2vec/")

u_mat <- read.table("umat.txt")
v_mat <- read.table("vmat.txt")
avg_mat <- read.table("avg_mat.txt")

name_vec <- read.table("names.txt")$V1

rownames(u_mat) <- name_vec
rownames(v_mat) <- name_vec
rownames(avg_mat) <- name_vec

mat_pcs <- prcomp(avg_mat)
# plot(mat_pcs$sdev^2 / sum(mat_pcs$sdev^2), type='o', ylab="Pct Variance", ylim=c(0, 1))

# jitter_amt = 0.00
# png("plot.png", width=851, height=755)
# plot(mat_pcs$x[, 1], mat_pcs$x[, 2], col="lightblue", cex=0.7, pch=19)
# text(jitter(mat_pcs$x[, 2], amount=jitter_amt) ~ jitter(mat_pcs$x[, 1], amount=jitter_amt), labels = name_vec, cex=0.8)
# text(mat_pcs$x[, 2] ~ mat_pcs$x[, 1], labels = name_vec, cex=0.8)
# dev.off()


## L2 Distance
# distance_mat <- matrix(NA, nrow=nrow(avg_mat), ncol=nrow(avg_mat))
# rownames(distance_mat) <- name_vec
# colnames(distance_mat) <- name_vec
# for (i in 1:nrow(avg_mat)) {
#   for (j in 1:nrow(avg_mat)) {
#     if (i == j) next
#     if (is.na(distance_mat[i, j])) {
#       vec_j <- unlist(avg_mat[j, ])
#       vec_i <- unlist(avg_mat[i, ])
#       temp <- dist(rbind(vec_i, vec_j))
#       distance_mat[i, j] <- temp
#       distance_mat[j, i] <- temp      
#     }
#   }
# }

#### Confusion Matrix ####
conf_mat <- read.table("confusion.txt")
colnames(conf_mat) <- c(as.character(name_vec), "UNK")
rownames(conf_mat) <- c(as.character(name_vec), "UNK")

## Predictions on Unknowns
unk_think <- conf_mat$UNK / sum(conf_mat$UNK)
names(unk_think) <- rownames(conf_mat)
cat("Unknown most commonly predicted as:\n")
rev(sort(unk_think))[1:8]
cat("\n\n")

cat(paste("% Correct:", round(100 * sum(diag(as.matrix(conf_mat))) / sum(as.matrix(conf_mat)), 2 ) )  )
cat("\n\n")


#### Cosine Distance ####
distance_mat <- matrix(NA, nrow=nrow(avg_mat), ncol=nrow(avg_mat))
rownames(distance_mat) <- name_vec
colnames(distance_mat) <- name_vec
for (i in 1:nrow(avg_mat)) {
  for (j in 1:nrow(avg_mat)) {
    if (i == j) next
    if (is.na(distance_mat[i, j])) {
      vec_j <- unlist(avg_mat[j, ])
      vec_i <- unlist(avg_mat[i, ])
      temp <- (vec_i %*% vec_j) / (sqrt(vec_i %*% vec_i) * sqrt(vec_j %*% vec_j))
      distance_mat[i, j] <- temp
      distance_mat[j, i] <- temp      
    }
  }
}

rm(i, j, vec_i, vec_j, temp)

furthest.n <- function(x, n) {
  l = length(x)
  temp <- sort(x)
  rev(tail(temp, n))
}

closest.n <- function(x, n) {
  l = length(x)
  temp <- sort(x)
  temp[1:n]
}

test_pokemon <- c("Landorus-Therian", "Clefable", "Tapu-Bulu",
                  "Hawlucha", "Swampert-Mega", "Sableye-Mega",
                  "Chansey", "Ribombee", "Ferrothorn", "Weavile", "Bisharp",
                  "Dragapult", "Pelipper", "Seismitoad", "Excadrill")
num_to_check = 10

for (poke in test_pokemon) {
  idx <- which(name_vec == poke)
  if (length(idx) == 0) next
  vec <- distance_mat[idx, ]
  closest <- closest.n(vec, num_to_check)
  closest.names <- names(closest)
  furthest <- furthest.n(vec, num_to_check)
  furthest.names <- names(furthest)
  
  cat(paste("Pokemon", poke))
  cat("\n")
  cat(paste("Closest:", paste(closest.names, round(closest, 3), collapse=" | ")))
  cat("\n")
  cat(paste("Furthest:", paste(furthest.names, round(furthest, 3), collapse=" | ")))
  cat("\n")
  cat("\n")
}

## Some metric of closeness
# apply(distance_mat, 1, mean, na.rm=T)