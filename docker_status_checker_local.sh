#!/bin/sh
echo "ID,,Image,,Command,,RunningFor,,Status,,Ports,,Names" > data/containers_status.csv
docker container ls -a --format {{.ID}},,{{.Image}},,{{.Command}},,{{.RunningFor}},,{{.Status}},,{{.Ports}},,{{.Names}} >> data/containers_status.csv