

# Kubernetes PodChaosMonkey

This repository contains a `Dockerfile` and associated Kubernetes configuration for a deployment that will randomly delete pods in a given namespace on a schedule. This is implemented in python (3.7.4).
 
An image built from the `Dockerfile` in this repository is available on Docker Hub as [`rd790/projects`](https://hub.docker.com/r/rd790/projects/).
 
The pod_choas_monkey Kubernetes configuration includes a ServiceAccount, Role and RoleBinding for accessing the Kubernetes API. There is also a configmap and CronJob used for the deployment, as well as offering some customisation.
 
### Configuration
 
You may need to set up credentials to access docker hub, use:
 
```bash
kubectl create secret docker-registry regcred --docker-username=<your-name> --docker-password=<your-pword> --docker-email=<your-email> -n <your-namespace>
```
 
Configuration for PodChaosMonkey is done via the exempt-labels-cm configmap and the pod-chaos-monkey CronJob:
 
* `exempt-labels-cm`: This configmap can be used to specify labels that you wish to be exempt from PodChaosMonkey.
I recommend keeping `nochaos: nochaos` as that's used on PodChaosMonkey itself.

#### Example of configmap
```yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: exempt-labels-cm
  namespace: workloads
data:
  nochaos: nochaos
  app: busybox
```

* `pod-chaos-monkey`: This CronJob is used for specifying a schedule, use as you normal word a cron job.
 
#### Example of CronJob

```yaml
---
apiVersion: batch/v1beta1 # batch/v1 for 1.21+
kind: CronJob
metadata:
  name: pod-chaos-monkey
  namespace: workloads
spec:
  schedule: "*/5 * * * *"
[... omitted ...]
```

Example Kubernetes config is included at [`config/kubernetes/pod_chaos_monkey/setup.yaml`](./config/kubernetes/pod_chaos_monkey/setup.yaml)
 
Example Kubernetes dummy workload is included at [`config/kubernetes/prod/prod.yaml`](./config/kubernetes/prod/prod.yaml)

### Example of PodChaosMonkey running 

```bash
NAME                                READY   STATUS              RESTARTS   AGE
busybox-5bc85cc8d9-5tgn7            1/1     Running             0          51m
busybox-5bc85cc8d9-ctfgs            1/1     Running             0          51m
nginx-deployment-66b6c48dd5-4tzv7   1/1     Running             0          4m28s
nginx-deployment-66b6c48dd5-rkxvz   1/1     Running             0          4m30s
nginx-deployment-66b6c48dd5-vxp7b   0/1     ContainerCreating   0          10s
pod-chaos-monkey-1670190600-7vw49   0/1     Completed           0          5m15s
pod-chaos-monkey-1670190900-knj6q   0/1     Completed           0          13s

$ kubectl logs pod-chaos-monkey-1670190900-knj6q
deleting pod nginx-deployment-66b6c48dd5-lnnv8 with namespace workloads
```


## How PodChaosMonkey works at a high level 

1. Scheduling happens when specified in the CronJob.
2. A dictionary of exempt labels are generated based on labels specified in the exempt-labels-cm configmap. 
3. A list of exempt pods is generated, using the previous list to identify pods that are exempt.
4. A list of pods eligible for deletion are generated by removing exempt pods from a list of all pods in the namespace. 
5. A random pod is deleted, this is done by generating a random number between 0 and the length of the previous list and executing the relevant delete api call. 
