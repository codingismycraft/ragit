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
# install vim9.0
cd
sudo apt-get purge vim
sudo apt-get autoremove
sudo apt update
sudo apt install xclip -y
wget https://ftp.nluug.nl/pub/vim/unix/vim-9.0.tar.bz2
tar -xvf vim-9.0.tar.bz2
sudo apt-get install libncurses5-dev libgtk2.0-dev libatk1.0-dev libcairo2-dev libx11-dev libxpm-dev libxt-dev python3-dev ruby-dev mercurial -y
sudo apt-get remove vim vim-runtime gvim vim-tiny vim-common vim-gui-common -y
cd vim90
./configure --with-features=huge --enable-multibyte --enable-rubyinterp --enable-python3interp --with-python-config-dir=/usr/lib/python3.9/config-3.9-x86_64-linux-gnu --enable-perlinterp --enable-luainterp --enable-gui=gtk2 --enable-cscope --prefix=/usr
sudo make install
cd
SCRIPT


Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"
  config.vm.provision "shell", inline: $script
  config.vm.provision "shell", path: "install-psql.sh"
  config.vm.network "forwarded_port", guest: 13131, host: 13131
  config.vm.synced_folder "/home/john/mygen-data", "/home/vagrant/mygen-data"
  config.vm.provider "virtualbox" do |vb|
    vb.name = "ragit"
    vb.memory = 8192
    vb.cpus = 2
  end
  config.vm.hostname = "ragit"
end
