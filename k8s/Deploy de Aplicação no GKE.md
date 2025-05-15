## ✅ **Passo a Passo: Deploy de Aplicação no GKE (TestBooster Web UI)**

### 🧱 **Pré-requisitos**

* Projeto no GCP: `testbooster`
* Cluster GKE: `testbooster-browser-use-cluster` criado na região `us-central1`
* Repositório Docker: `us-east1-docker.pkg.dev/testbooster/testbooster-browser-use/testbooster-browser-use`
* Imagem Docker já publicada (`:latest`)
* `.env` com variáveis de ambiente na raiz do projeto

---

### 🔐 **1. Autenticação e configuração do projeto**

```powershell
gcloud auth login
gcloud config set project testbooster
```

---

### 🔗 **2. Conectar ao cluster GKE**

```powershell
gcloud container clusters get-credentials testbooster-browser-use-cluster --region us-central1
```

---

### 🔑 **3. Conceder permissão ao cluster para acessar Artifact Registry**

```powershell
$PROJECT_NUMBER = gcloud projects describe testbooster --format="value(projectNumber)"

gcloud artifacts repositories add-iam-policy-binding testbooster-browser-use `
  --location=us-east1 `
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
  --role="roles/artifactregistry.reader"
```

---

### 📦 **4. Criar o Secret com variáveis de ambiente**

```powershell
kubectl delete secret testbooster-browser-use-env --ignore-not-found

kubectl create secret generic testbooster-browser-use-env --from-env-file .\.env
```

---

### 📄 **5. Criar os manifestos Kubernetes**

**deployment.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: testbooster-browser-use
spec:
  replicas: 1
  selector:
    matchLabels:
      app: testbooster-browser-use
  template:
    metadata:
      labels:
        app: testbooster-browser-use
    spec:
      containers:
      - name: browser-use
        image: us-east1-docker.pkg.dev/testbooster/testbooster-browser-use/testbooster-browser-use:latest
        ports:
        - containerPort: 7788
        envFrom:
        - secretRef:
            name: testbooster-browser-use-env
```

**service.yaml**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: testbooster-browser-use
spec:
  type: LoadBalancer
  selector:
    app: testbooster-browser-use
  ports:
  - port: 80
    targetPort: 7788
```

---

### 🚀 **6. Aplicar deployment e service**

```powershell
kubectl apply -f .\k8s\deployment.yaml
kubectl apply -f .\k8s\service.yaml
```

---

### 🔁 **7. Acompanhar rollout**

```powershell
kubectl rollout status deployment/testbooster-browser-use
```

---

### 🌐 **8. Obter IP externo da aplicação**

```powershell
kubectl get svc testbooster-browser-use
```

Acesse via:

```
http://<EXTERNAL-IP>/
```

---

### 🛠️ **9. (Opcional) Monitorar logs em tempo real**

```powershell
kubectl logs -l app=testbooster-browser-use -f
```



# Processo Resumido:
1. Atualize a versão da imagem no k8s\deployment.yaml
docker build -f Dockerfile -t us-east1-docker.pkg.dev/testbooster/testbooster-browser-use/testbooster-browser-use:0.0.5 .
gcloud auth configure-docker us-east1-docker.pkg.dev
docker push us-east1-docker.pkg.dev/testbooster/testbooster-browser-use/testbooster-browser-use:0.0.5
gcloud container clusters get-credentials testbooster-browser-use-cluster --region us-central1 --project testbooster
# 1) Pega o número do projeto
$projectNumber = gcloud projects describe testbooster --format="value(projectNumber)"
# 2) Dá permissão ao nó do GKE ler o Artifact Registry
gcloud artifacts repositories add-iam-policy-binding testbooster-browser-use `
  --location=us-east1 `
  --member="serviceAccount:$projectNumber-compute@developer.gserviceaccount.com" `
  --role="roles/artifactregistry.reader"

`(se teve alteração/criação de variável de ambiente): `kubectl delete secret testbooster-browser-use-env --ignore-not-found
`(se teve alteração/criação de variável de ambiente): `kubectl create secret generic testbooster-browser-use-env --from-env-file ./.env

´Alterar o número da imagem no k8s\deployment.yaml 
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

