$script = <<SCRIPT
sudo apt update
sudo apt install python3-pip -y
sudo apt-get install libpq-dev python3-dev -y
mkdir -p /home/vagrant/mygen-data
chown vagrant:vagrant /home/vagrant/mygen-data
sudo apt install postgresql postgresql-contrib -y
SCRIPT


Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"
  config.vm.provision "shell", inline: $script
  config.vm.hostname = "mygenai"
  config.vm.provision "shell", path: "install-psql.sh"
  config.vm.synced_folder "/home/john/mygen-data", "/home/vagrant/mygen-data"
  config.vm.provider "virtualbox" do |vb|
    vb.name = "mygenai"
  end
end
