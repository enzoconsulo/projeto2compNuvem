Vagrant.configure("2") do |config|
  # --- Sistema Base ---
  config.vm.box = "ubuntu/jammy64"
  config.vm.hostname = "projeto2"

  # --- Recursos da VM ---
  config.vm.provider "virtualbox" do |vb|
    vb.name = "projeto2"
    vb.memory = 4096
    vb.cpus = 2
  end

  # --- Rede ---
  # Porta 8080 do host → 5000 da VM (Flask)
  config.vm.network "forwarded_port", guest: 5000, host: 8080, auto_correct: true

  # --- Pasta sincronizada ---
  # A pasta do projeto (no seu computador) será montada dentro da VM
  config.vm.synced_folder "./projeto2", "/home/vagrant/projeto2"

  # --- Provisionamento automático ---
  config.vm.provision "shell", inline: <<-SHELL
    echo "=== Atualizando pacotes ==="
    apt-get update -y

    echo "=== Instalando Python e Flask ==="
    apt-get install -y python3 python3-pip git
    pip3 install flask

    echo "=== Criando serviço systemd para o Flask ==="
    cat <<EOF > /etc/systemd/system/flaskapp.service
[Unit]
Description=Flask App
After=network.target

[Service]
User=vagrant
WorkingDirectory=/home/vagrant/projeto2
ExecStart=/usr/bin/python3 /home/vagrant/projeto2/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    echo "=== Habilitando serviço Flask ==="
    systemctl daemon-reload
    systemctl enable flaskapp
    systemctl start flaskapp

    echo "=== Tudo pronto! Acesse em: http://localhost:8080 ==="
  SHELL
end
