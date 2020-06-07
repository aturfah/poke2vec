echo "Hello!"

echo "Pulling down real teams from replays"
python get_ream_teams.py

echo "Pulling data from smogon servers"
python pull_data.py

echo "Generating teams..."
python generate_teams.py

echo "Fitting vector embeddings"
python fit_model.py

echo "Postprocessing"
python postprocess.py

echo "Running KL Divergence Sanity Checks"
echo "::Marginal"
Rscript sanity\ checks/marginal_sanity_check.R 
echo "::Conditional"
Rscript sanity\ checks/cond_sanity_check.R 

echo "Getting Vector Clusters"
Rscript analysis.R