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
plot(mat_pcs$sdev^2 / sum(mat_pcs$sdev^2), type='o', ylab="Pct Variance", ylim=c(0, 1))

jitter_amt = 0.00
png("plot.png", width=851, height=755)
plot(mat_pcs$x[, 1], mat_pcs$x[, 2], col="lightblue", cex=0.7, pch=19)
# text(jitter(mat_pcs$x[, 2], amount=jitter_amt) ~ jitter(mat_pcs$x[, 1], amount=jitter_amt), labels = name_vec, cex=0.8)
text(mat_pcs$x[, 2] ~ mat_pcs$x[, 1], labels = name_vec, cex=0.8)
dev.off()