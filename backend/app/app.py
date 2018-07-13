from flask import Flask
from flask import jsonify
from flask import request
from werkzeug.contrib.fixers import ProxyFix
import git
import docker
import json
import os
import subprocess
import shutil
from datetime import datetime, timedelta
from gevent.pywsgi import WSGIServer


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

def getCfg():
    with open(configURI) as f:
        config = json.load(f)
    return config

def getInstancesDir():
    return os.path.join(os.getcwd(), "instances")

def exceptionAsDict(ex, context):
    return dict(exception=str(ex),context=context)

def listInstanceFolders():
    return os.listdir(getInstancesDir())

def getInstanceInfo(instanceName):
    try:
        instanceDir = os.path.join(getInstancesDir(), instanceName)
        if not os.path.exists(instanceDir):
            raise Exception('The instance ' + instanceName + " does not exist")
        serviceList = client.services.list()
        print(client.services.list())
        serviceInfoList = {}
        for service in serviceList:
            if str(service.name).startswith(instanceName+"_"):
                serviceInfo = {}
                serviceInfo['short_id'] = service.short_id
                serviceInfo['name'] = service.name
                serviceInfo['id'] = service.id
                serviceInfoList[serviceInfo['name']] = serviceInfo
        return serviceInfoList
    except Exception as e:
        return exceptionAsDict(e, "get Instance Infos")

def addSecsToTime(timeval, secs_to_add):
    return timeval + timedelta(seconds=secs_to_add)

configURI = os.path.join(getInstancesDir(), "config.json")


# https://github.com/docker/docker-py/issues/1173
def startInstance(dir ,name):
    #TODO: Push to local registry before!
    #TODO: apply the settings and rewrite the images to point to local registry
    subprocess.run(['docker-compose',
                    'build',
                    '-f',
                    os.path.join(dir, 'docker-compose.yml'),
                    '-p',
                    name
                    ],
                   stdout=subprocess.PIPE)
    subprocess.run(['docker',
                    'stack',
                    'deploy',
                    '--compose-file',
                    os.path.join(dir, 'docker-compose.yml'),
                    name],
                   stdout=subprocess.PIPE)

def stopInstance(name):
    subprocess.run(['docker',
                    'stack',
                    'down',
                    name],
                   stdout=subprocess.PIPE)
    timeout = addSecsToTime(datetime.now(), 60)
    stoppedAllContainer = False
    while datetime.now() < timeout:
        for container in client.containers.list():
            if container.status == 'running':
                if str(container.name).startswith(name + "_"):
                    container.kill()
                    break
                else:
                    stoppedAllContainer = True
        if stoppedAllContainer:
            break
    if not stoppedAllContainer:
        raise Exception('Timout during stopping of containers for instance ' + name + ' was reached')

app = Flask(__name__)

@app.route("/")
def status():
    return jsonify("{name: 'Hello World'}")

@app.route("/get_instances")
def listInstances():
    try:
        instanceList = listInstanceFolders()
        instances = {}
        i = 0
        for instance in instanceList:
            instances[i] = instance
            i = i + 1
        return jsonify(instances)
    except Exception as e:
        return jsonify(exceptionAsDict(e, "Get All Instances"))

@app.route("/get_instance_info")
def listInstanceInfo():
    name = request.args.get('name', default='foo', type=str)
    return jsonify(getInstanceInfo(name))

@app.route("/get_all_volumes")
def listAllVolumes():
    try:
        volume_list = client.volumes.list()
        volumes = {}
        for volumeEntry in volume_list:
            volume = {}
            volume['id'] = volumeEntry.id
            volume['short_id'] = volumeEntry.short_id
            volume['name'] = volumeEntry.name
            volume['attrs'] = volumeEntry.attrs
            volumes[volume['id']] = volume
        return jsonify(volumes)
    except Exception as e:
        return jsonify(exceptionAsDict(e, "Get All Volumes"))

@app.route("/config")
def printCfg():
    return jsonify(getCfg())

'''
Needs 2 Parameters:
  name: The name of the instance
  type: the type of the instance (read from config)
'''
@app.route("/create_instance")
def create_instance():
    try:
        name = request.args.get('name', default='foo', type=str)
        type = request.args.get('type', default='standard', type=str)
        instances = getCfg()['instances']
        if type not in instances:
            raise Exception("The type " + type + " is not in config.json")
        instanceConfig = instances[type]
        repoURL = instanceConfig['repo']
        branchName = instanceConfig['branch']
        commitSHA = instanceConfig['commit']
        if os.path.isdir(os.path.join(getInstancesDir(), name)):
            raise Exception("The Instance with the name " + name + " already exists")
        repoDir = os.path.join(getInstancesDir(), name)
        os.makedirs(repoDir)
        repo = git.Repo.clone_from(repoURL, repoDir)
        repo_heads = repo.heads
        repo_heads_names = [h.name for h in repo_heads]
        if branchName not in repo_heads_names:
            raise Exception("The " + branchName + " is not a branch in the selected repository")
        repo_heads[branchName].checkout()
        repo.commit(commitSHA)
        startInstance(repoDir, name)
        return jsonify(getInstanceInfo(name))
    except Exception as e:
        return jsonify(exceptionAsDict(e, "Create Instance"))

@app.route('/shutdown_instance')
def shutdownInstance():
    name = request.args.get('name', default='foo', type=str)
    stopInstance(name)
    return jsonify('{"status": "Instance halted"}')

@app.route('/remove_instance')
def removeInstance():
    try:
        name = request.args.get('name', default='foo', type=str)
        stopInstance(name)
        client.containers.prune()
        for container in client.containers.list():
            if str(container.name).startswith(name+"_"):
                container.remove()
        timeout = addSecsToTime(datetime.now(), 30)
        deletedAllContainer = False
        while datetime.now() < timeout:
            for container in client.containers.list():
                if str(container.name).startswith(name + "_"):
                    break
                else:
                    deletedAllContainer = True
                    break
            if deletedAllContainer:
                break
        if not deletedAllContainer:
            raise Exception('Timout during deletion of containers for instance '+ name +' was reached')
        for volume in client.volumes.list():
            if str(volume.name).startswith(name+"_"):
                print("Removing Volume " + volume.name)
                volume.remove(force=True)
        for network in client.networks.list():
            if str(network.name).startswith(name+"_"):
                print("Removing Network " + network.name)
                network.remove()
        repoDir = os.path.join(getInstancesDir(), name)
        shutil.rmtree(repoDir)
        return jsonify('{"status": "Instance removed"}')
    except Exception as e:
        return jsonify(exceptionAsDict(e, "Remove Instance"))


if __name__ == "__main__":
    print("Starting WSGI Server on Port 7000")
    server = WSGIServer(('', 7000), app)
    server.serve_forever()

