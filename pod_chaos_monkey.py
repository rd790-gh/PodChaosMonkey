from kubernetes import client, config
import sys
import os
from random import randrange
import os

# This script will delete a random pod, you can define what pods are exempt by using a config map
# To schedule this, use the CronJob schedule function.


# Sets up your credentials, uses the defined ServiceAccount
config.load_incluster_config()

# ​​Uses environment variables specified in the deployment manifest
namespace = os.environ['MY_POD_NAMESPACE']
configmap = os.environ['EXEMPT_LABELS']


def get_labels_to_avoid(namespace, name):
    """
   This pulls data from the configmap
   It then returns the data as a dict for later use

   Args:
       namespace (STR): Namespace we're interesting in
       name (str): the configmap that will allow users to specify
       which labels are exempt from PodChaosMonkey. 

   Returns:
       Dict: A dict of the labels that the use wants exempt from deletion
    """
    v1 = client.CoreV1Api()
    config = v1.read_namespaced_config_map(name, namespace)
    return config.data


def get_pods_that_are_exempt(namespace, labels):
    """
    Checked to see which pods have the exempt labels and adds them to a list

    Args:
        namespace (str): Namespace we're interesting in 
        labels (dict): dict of labels that are exempt from deletion

    Returns:
        list: List of pods that should be exempt from deletion
    """
    v1 = client.CoreV1Api()
    pods_exempt = []
    for key, value in labels.items():
        result = v1.list_namespaced_pod(
            namespace, label_selector=f"{key}={value}", watch=False)
        for pod in result.items:
            pods_exempt.append(pod.metadata.name)
    return pods_exempt


def get_pods_to_delete(namespace, pods_exempt):
    """
   This gets a list of pods in the namespace, then it removes the pods that
   are exempt from deletion from the list. It returns a list containing pods that are eligible for deletion

   Args:
       namespace (str): Namespace we're interesting in
       labels (dict): dict of labels pods contain, which we wish to avoid deleting
   Returns:
       list: Returns a list with all the pods eligible for deletion
    """
    v1 = client.CoreV1Api()
    pods_able_to_delete = []

    pod_list = v1.list_namespaced_pod(namespace=namespace)
    for pod in pod_list.items:
        pods_able_to_delete.append(pod.metadata.name)

    pods_to_delete = [i for i in pods_able_to_delete if i not in pods_exempt]

    return pods_to_delete


def delete_pod(namespace, pods_to_delete):
    """ 
   Delete a pod based on its name and namespace.
   The pod is deleted without a graceful period to trigger an abrupt
   termination.

   Args:
       namespace (str): Namespace we're interesting in
       pods_to_delete (list): a list containing the pods names that are at eligible for deletion
    Returns: Details on pod deleted.
    """
    v1 = client.CoreV1Api()
    len_of_pods_to_delete = len(pods_to_delete)
    random_pod = randrange(len_of_pods_to_delete)

    print(
        f'deleting pod {pods_to_delete[random_pod]} with namespace {namespace}')

    delete = v1.delete_namespaced_pod(
        name=pods_to_delete[random_pod], body=client.V1DeleteOptions(), namespace=namespace)
    return delete


labels_dict = get_labels_to_avoid(namespace=namespace, name=configmap)

pods_exempt_list = get_pods_that_are_exempt(
    namespace=namespace, labels=labels_dict)

pods_to_delete_list = get_pods_to_delete(
    namespace=namespace, pods_exempt=pods_exempt_list)

# Delete pod
delete_pod(namespace, pods_to_delete_list)
