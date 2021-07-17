wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update
sudo apt-get install sublime-text
apt-get install python3-pip
pip install selenium
pip install xlsxwriter
sudo cp geckodriver /usr/bin/
sudo chmod 777 /usr/bin/geckodriver
echo
echo "program çalışmaya hazır"
echo
