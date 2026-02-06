#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Dependencies
pip install -r requirements.txt

# 2. Collect Static Files
python manage.py collectstatic --no-input

# 3. Run Migrations (Create Tables)
python manage.py migrate

# 4. Load Data (This imports your products from the file)
# Note: Ensure you pushed datadump.json to GitHub!
if [ -f "datadump.json" ]; then
    echo "Loading data from datadump.json..."
    python manage.py loaddata datadump.json
fi

# 5. Create Superuser (Run the script we just made)
python create_superuser.py