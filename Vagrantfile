$script = <<SCRIPT
sudo apt update
sudo apt install python3-pip -y
sudo apt-get install libpq-dev python3-dev -y
SCRIPT


Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"
  config.vm.provision "shell", inline: $script
  config.vm.hostname = "mygenai"
  config.vm.network "forwarded_port", guest: 8501, host: 18501
  config.vm.provider "virtualbox" do |vb|
    vb.name = "mygenai"
  end
end
