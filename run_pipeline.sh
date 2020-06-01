echo "Hello!"

echo "Pulling data from smogon servers"
python pull_data.py

echo "Generating teams..."
python generate_teams.py

echo "Running KL Divergence Sanity Checks"
echo "::Marginal"
Rscript sanity\ checks/marginal_sanity_check.R 
echo "::Conditional"
Rscript sanity\ checks/cond_sanity_check.R 

echo "Fitting vector embeddings"
python fit_model.py

echo "Postprocessing"
python postprocess.py
