Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.hostname = "projeto2"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "projeto2"
    vb.memory = 4096
    vb.cpus = 2
  end

  config.vm.network "forwarded_port", guest: 80, host: 8080, auto_correct: true
  config.vm.network "private_network", ip: "192.168.56.10"

  config.vm.synced_folder "./projeto2", "/home/vagrant/projeto2"

  config.vm.provision "shell", inline: <<-SHELL
    set -e

    apt-get update -y

    apt-get install -y locales python3 python3-pip git apache2 libapache2-mod-wsgi-py3 \
                       systemd psmisc curl dos2unix

    locale-gen en_US.UTF-8
    update-locale LANG=en_US.UTF-8
    export LANG=en_US.UTF-8
    export LC_ALL=en_US.UTF-8

    pip3 install --ignore-installed -r /home/vagrant/projeto2/requirements.txt || true

    mkdir -p /home/vagrant/projeto2/logs
    mkdir -p /home/vagrant/projeto2/scripts
    chmod o+x /home
    chmod o+x /home/vagrant
    chown -R www-data:www-data /home/vagrant/projeto2
    chmod -R 755 /home/vagrant/projeto2

    if [ -d /home/vagrant/projeto2/scripts ]; then
      find /home/vagrant/projeto2/scripts -type f -name "*.sh" -exec dos2unix {} \\; 2>/dev/null
      chmod +x /home/vagrant/projeto2/scripts/*.sh || true
    fi

    cat <<'EOF' > /etc/apache2/sites-available/projeto2.conf
<VirtualHost *:80>
    ServerName localhost
    DocumentRoot /home/vagrant/projeto2

    WSGIDaemonProcess projeto2 python-home=/usr/bin/python3 python-path=/home/vagrant/projeto2
    WSGIScriptAlias / /home/vagrant/projeto2/app.wsgi

    <Directory /home/vagrant/projeto2>
        Options +ExecCGI +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/projeto2-error.log
    CustomLog ${APACHE_LOG_DIR}/projeto2-access.log combined
</VirtualHost>
EOF

    a2dissite 000-default.conf || true
    a2ensite projeto2.conf
    systemctl enable apache2
    systemctl restart apache2

    cat <<'EOF2' > /etc/systemd/system/backend_daemon.service
[Unit]
Description=Backend Executor (namespaces + cgroups) para Projeto2
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/vagrant/projeto2/backend_daemon.py
Restart=always
User=root
WorkingDirectory=/home/vagrant/projeto2
Environment=LANG=en_US.UTF-8
Environment=LC_ALL=en_US.UTF-8

[Install]
WantedBy=multi-user.target
EOF2
    systemctl daemon-reload
    systemctl enable backend_daemon
    systemctl restart backend_daemon
  SHELL
end
