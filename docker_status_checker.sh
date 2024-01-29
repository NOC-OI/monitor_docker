#!/bin/sh
echo "ID,,Image,,Command,,RunningFor,,Status,,Ports,,Names" > /home/gitlab-runner/monitor_docker/data/containers_status.csv
docker container ls -a --format {{.ID}},,{{.Image}},,{{.Command}},,{{.RunningFor}},,{{.Status}},,{{.Ports}},,{{.Names}} >> /home/gitlab-runner/monitor_docker/data/containers_status.csv
docker cp /home/gitlab-runner/monitor_docker/data/containers_status.csv monitor_docker:/data/