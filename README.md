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

## Docker:

### Download Docker Desktop (only once):
follow the instructions: https://www.docker.com/products/docker-desktop/

### Connect to Docker Hub:
```
docker login
```
### Build Docker image locally:
```
docker build -f deployments/models/dummy/Dockerfile -t detector-server:dummy .
```

### Tag your image for the registry:
```
docker tag detector-server:dummy yotam56/detector-server:dummy
```

### Push the image to Docker Hub:
```
docker push yotam56/detector-server:dummy
```

## K8S:

### install minikube (only once):

follow the instructions: https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Fx86-64%2Fstable%2Fbinary+download

### Connect k8s to Docker Hub:
```
kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=<your-dockerhub-username> \
  --docker-password=<your-dockerhub-password> \
  --docker-email=<your-email>
```

### Run minikube:
`minikube start`

### Apply k8s resources:
```
kubectl apply -f deployments/models/dummy/k8s/deployment.yaml
kubectl apply -f deployments/models/dummy/k8s/service.yaml
```

### Expose the load balancer:
```
minikube tunnel
```
now you can use `kubectl get services` to see the "EXTERNAL-IP" to communicate with your service.
for example: `curl -X GET "http://127.0.0.1:8000/colab_hello"`
