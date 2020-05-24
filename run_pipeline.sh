echo "Hello!"

echo "Pulling data from smogon servers"
python pull_data.py

echo "Generating teams..."
python generate_teams.py

echo "Fitting vector embeddings"
python fit_model.py

echo "Postprocessing"
python postprocess.py
