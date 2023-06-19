# Testing

Local VSCode: In VS code get the Shiny plugin which will allow you to run Shiny apps in VS code.
Local Docker: 
export IMAGE=shiny-demo:0.1
docker build -t $IMAGE .
docker run -p 8080:8080 $IMAGE
Go to http://127.0.0.1:8080 in your browser and check.


Deployment to Azure:
az acr build --registry acrshinydemo --resource-group rg-shiny-demo --image shiny-demo-app .