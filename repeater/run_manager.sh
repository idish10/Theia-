#
# PURPOSE:
# 
# Run the tracking/logging manager iterativley using cron.
# 
# USAGE:
#
#   Add the following line to /var/spool/cron/crontabs/{USER} :
#
#   m h d m dw
#   * * * * * {PATH}/run_manager.sh >> /tmp/stdout.log 2>> /tmp/stderr.log
#
#   Or use crontab -e to add it manually
# 

docker pull pattrncapital/robust-tracking-manager

docker run -v /var/run/docker.sock:/var/run/docker.sock pattrncapital/robust-tracking-manager

docker rmi -f $(docker images -a -q)
docker rm $(docker ps -a --filter status=exited -q)
docker rmi -f $(docker images -a -q)
docker rm $(docker ps -a --filter status=exited -q)
