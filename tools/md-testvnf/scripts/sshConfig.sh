#!/bin/bash -eux
sudo mv temp /home/testvnf/authorized_keys
sudo mkdir /home/testvnf/.ssh 
sudo mv /home/testvnf/authorized_keys /home/testvnf/.ssh/
sudo chmod 700 /home/testvnf/.ssh
sudo chmod 600 /home/testvnf/.ssh/authorized_keys
sudo chown testvnf /home/testvnf/.ssh
sudo chown testvnf /home/testvnf/.ssh/authorized_keys
# Add `sync` so Packer doesn't quit too early, before the large file is deleted.
sync