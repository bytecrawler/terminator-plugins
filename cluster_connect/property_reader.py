import json
import os

pluginpath = os.path.dirname(os.path.realpath(__file__))
configpath = (pluginpath + "/cluster_connect_config")

for root, dirs, files in os.walk(configpath):
    for file in files:
        if file.endswith(".json"):
            filename = (os.path.join(root, file))
            with open(filename) as data_file:
                try:
                    CLUSTERS
                except NameError:
                    CLUSTERS = json.load(data_file)
                else:
                    CLUSTERS.update(json.load(data_file))


def read_groups():
    clusters = CLUSTERS.keys()
    clusters.sort()
    groups = []
    for cluster in clusters:
        group = get_property(cluster, 'group', 'none')
        if group != 'none' and group not in groups:
            groups.append(group)
    return groups


def get_property(cluster, prop, default=False):
    # Check if property and Cluster exsist and return if true else return false
    if CLUSTERS.has_key(cluster) and CLUSTERS[cluster].has_key(prop):
        return CLUSTERS[cluster][prop]
    else:
        return default


def get_clusters():
    return CLUSTERS.keys()
