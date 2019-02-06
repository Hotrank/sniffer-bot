sudo apt update

# Get Miniconda and make it the main Python interpreter
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p ~/miniconda
rm ~/miniconda.sh
echo "PATH=$PATH:$HOME/miniconda/bin" >> .bashrc
source .bashrc

sudo apt install git
conda create --name tf tensorflow python=3.5
source activate tf
conda install pillow
conda install requests
conda install -c anaconda mysqlclient
sudo apt-get install libzmq3-dev
conda install -c anaconda pyzmq
git clone https://github.com/Hotrank/drug_detect.git
