# Alerts Server
An orchestrator server designed to analyze given frames and send alerts based on the severity policy.

# Prerequisite:

python version: `3.11.4` (recommended to use `pyenv` to manage multiple Python versions)

## installing venv:
Installing virtualenv - requir only once:
`python3 -m pip install --user virtualenv`

Install the venv on your repository:
Enter your repository path in terminal and run the following command:
`python3 -m venv venv`

ativate the venv in your terminal: 
`source venv/bin/activate`

## installing requirments:
first, make sure you have pip installed

install requirments:
`pip install -r requirements.txt`

## Contributing:
Please use pre-commit before pushing to master.

On first time run:
`pre-commit install --install-hooks -t pre-commit -t commit-msg`
## set you own OpenAI key as enviroment variable
for example: `export OPENAI_API_KEY=<your_api_key_here>`
