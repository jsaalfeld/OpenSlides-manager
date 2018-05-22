# Multi instance backend for OpenSlides

This is meant to run in a Docker Swarm. Therefore you should setup your
machine(s) in a swarm, which is fairly simple. For a single machine you just
define your swarm master via

    docker swarm init --advertise-addr <your-ip-address>

If you want to join an additional worker to your swarm, you have to generate a
token on your master node via

    docker swarm join-token

and then join the worker on the worker machine via

    docker swarm join --token <your-token> <masters-ip-adress>:<masters-port:default:2377>


Then we need some authentication:

    docker run  --entrypoint htpasswd registry:2 -Bbn <username> <password> > nginx/htpasswd

This creates a htpasswd file. You can also create it in different ways,
the important thing here is, that the htpasswd file has to be
```nginx/htpasswd```. (The Standard username:password combination is
```openslides:openslides```)

We want to run the registry on the main node only. For that we search for the
name of your main node with ```docker node ls``` and then execute the following
to fullfill the constraint:

    docker node update --label-add registry=true <nodename>

## Deploy the Manager

You should deploy the Manager on the master node only!

First we need to define the master node. For that we search for the
name of your main node with ```docker node ls``` and then execute the following
to fullfill the constraint:

    docker node update --label-add master=true <nodename>

You build the manager first via

    docker-compose build

and deploy the master to your swarm

    docker stack deploy --compose-file docker-compose.yml manager

Now everything should be up and running, so you can log in your master
and your nodes to the now deployed docker registry via

    docker login <your-swarm-domain>:443 --username <username> --password <password>
