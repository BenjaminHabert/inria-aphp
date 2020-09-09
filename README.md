# inria-aphp

réponse à l'exercice https://github.com/agramfort/inria-aphp-assignment


# Setup

```
git clone https://github.com/BenjaminHabert/inria-aphp.git
cd inria-aphp

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# lint and test
flake8 aphp/
python -m pytest

# running notebooks
export PYTHONPATH=$PYTHONPATH:$(pwd)
jupyter notebook
```
