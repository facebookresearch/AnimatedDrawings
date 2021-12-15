#!/bin/bash

#INSTALL ECS AGENT
sudo sh -c "echo 'net.ipv4.conf.all.route_localnet = 1' >> /etc/sysctl.conf"
sudo sysctl -p /etc/sysctl.conf

#ENABLE IAM ROLES FOR TASKS
echo iptables-persistent iptables-persistent/autosave_v4 boolean true | sudo debconf-set-selections
echo iptables-persistent iptables-persistent/autosave_v6 boolean true | sudo debconf-set-selections
sudo apt-get install iptables-persistent
sudo iptables -t nat -A PREROUTING -p tcp -d 169.254.170.2 --dport 80 -j DNAT --to-destination 127.0.0.1:51679
sudo iptables -t nat -A OUTPUT -d 169.254.170.2 -p tcp -m tcp --dport 80 -j REDIRECT --to-ports 51679

sudo iptables -A INPUT -i eth0 -p tcp --dport 51678 -j DROP
sudo sh -c 'iptables-save > /etc/iptables/rules.v4'




#HOST VOLUME MOUNT POINTS
sudo mkdir -p /var/log/ecs /var/lib/ecs/data

#CREATE DOCKER USER
sudo docker load --input ./ecs-agent.tar && rm ecs-agent.tar
sudo groupadd docker
sudo usermod -aG docker $USER

#CREATE ECS CONFIG
sudo mkdir -p /etc/ecs && sudo touch /etc/ecs/ecs.config

sudo bash -c 'cat <<'EOF' > /etc/ecs/ecs.config
ECS_CLUSTER=prod_cluster
ECS_ENABLE_GPU_SUPPORT=true
ECS_NVIDIA_RUNTIME=nvidia
ECS_DATADIR=/data
ECS_ENABLE_AWSLOGS_EXECUTIONROLE_OVERRIDE=true
ECS_ENABLE_TASK_IAM_ROLE=true
ECS_AVAILABLE_LOGGING_DRIVERS=["json-file","syslog","awslogs","none"]
EOF'

# SET UP NVIDIA RUNTIME FOR DOCKER DAEMON
sudo cat <<"EOF" > /etc/docker/daemon.json
{
  "default-runtime": "nvidia",
  "runtimes": {
      "nvidia": {
        "path": "/etc/docker-runtimes.d/nvidia"
      }
  }
}
EOF

# SET UP NVIDIA GPU INFO
sudo mkdir -p /var/lib/ecs/gpu/
sudo touch /var/lib/ecs/gpu/nvidia-gpu-info.json

# REGISTER GPUs WITH ECS
DRIVER_VERSION=$(modinfo nvidia --field version)
IDS=$(nvidia-smi -L | cut -f6 -d " " | cut -c 1-40)
sudo -E bash -c 'echo -e "{\"DriverVersion\":\"'$DRIVER_VERSION'\",\"GPUIDs\":[\"'$IDS'\"]}" >>  /var/lib/ecs/gpu/nvidia-gpu-info.json'
nvidia-modprobe -u -c=0




#sudo bash -c 'cat <<'EOF' > ecs_agent_restart.sh
#docker kill $(docker ps | grep ecs-agent | awk '{print $1}' | tail -n1)
#docker container prune -f 
#EOF'

#sudo chmod u+x ecs_agent_restart.sh

#CONTAINER AGENT
curl -o ecs-agent.tar https://s3.amazonaws.com/amazon-ecs-agent-us-east-1/ecs-agent-latest.tar
sudo docker load --input ./ecs-agent.tar
sudo docker run --name ecs-agent \
--detach=true \
--restart=on-failure:10 \
--volume=/var/run:/var/run \
--volume=/var/log/ecs/:/log \
--volume=/var/lib/ecs/data:/data \
--volume=/etc/ecs:/etc/ecs \
--device /dev/nvidiactl:/dev/nvidiactl \
--device /dev/nvidia-uvm:/dev/nvidia-uvm \
--volume=/var/lib/ecs/gpu:/var/lib/ecs/gpu \
--net=host \
--env-file=/etc/ecs/ecs.config \
amazon/amazon-ecs-agent:latest