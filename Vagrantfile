$script = <<SCRIPT
sudo apt update
sudo apt install python3-pip -y
sudo apt-get install libpq-dev python3-dev -y
mkdir -p /home/vagrant/mygen-data
chown vagrant:vagrant /home/vagrant/mygen-data
sudo apt install postgresql postgresql-contrib -y
echo "export PYTHONPATH='/vagrant' " >> /home/vagrant/.bashrc
echo "alias pt=/vagrant/pt.sh" >> /home/vagrant/.bashrc
sudo pip3 install -r /vagrant/requirements.txt
# install vim gtk to make clipboard interaction simpler.
cd
sudo apt update
sudo apt-get purge vim
sudo apt-get autoremove
sudo apt update
sudo apt install xclip -y
sudo apt install vim-gtk3 -y

# Clone dotfiles if needed
DOTFILES_DIR=$HOME_DIR/dotfiles
if [ ! -d "$DOTFILES_DIR" ]; then
  git clone git@github.com:codingismycraft/dotfiles.git $DOTFILES_DIR
fi

cd dotfiles
./install_light.sh
cd
SCRIPT


Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"
  config.vm.provision "shell", inline: $script
  config.vm.provision "shell", path: "install-psql.sh"
  config.ssh.forward_agent = true # Used for Clipboard sharing.
  config.ssh.forward_x11 = true # Used for Clipboard sharing.
  config.vm.network "forwarded_port", guest: 13131, host: 13131
  config.vm.synced_folder "/home/john/mygen-data", "/home/vagrant/mygen-data"
  config.vm.provider "virtualbox" do |vb|
    vb.name = "ragit"
    vb.memory = 8192
    vb.cpus = 2
    # Used for Clipboard sharing.
    vb.customize ['modifyvm', :id, '--clipboard', 'bidirectional'] 
  end
  config.vm.hostname = "ragit"
  config.ssh.forward_agent = true
  config.ssh.forward_x11 = true
end
