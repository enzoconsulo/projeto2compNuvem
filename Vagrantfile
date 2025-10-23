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
  # Agora o host:8000 -> guest:8000 (Apache)
  config.vm.network "forwarded_port", guest: 80, host: 8080, auto_correct: true

  # --- Pasta sincronizada ---
  config.vm.synced_folder "./projeto2", "/home/vagrant/projeto2"

  # --- Provisionamento automático ---''
  config.vm.provision "shell", inline: <<-SHELL
    set -e
    echo "=== Atualizando pacotes ==="
    apt-get update -y
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

    echo "=== Instalando pacotes necessários ==="
    apt-get install -y python3 python3-venv python3-pip git apache2 libapache2-mod-wsgi-py3 build-essential
    echo "=== Pacotes instalados ==="

    # módulos apache a habilitar mais tarde
    a2enmod proxy proxy_http headers rewrite

    # criar virtualenv como usuário vagrant
    if [ ! -d /home/vagrant/venv ]; then
      echo "=== Criando virtualenv em /home/vagrant/venv ==="
      sudo -u vagrant -H python3 -m venv /home/vagrant/venv
    fi

    # instalar dependências no venv (usar requirements.txt se existir)
    if [ -f /home/vagrant/projeto2/requirements.txt ]; then
      echo "=== Instalando dependências do requirements.txt ==="
      sudo -u vagrant -H /home/vagrant/venv/bin/pip install --upgrade pip
      sudo -u vagrant -H /home/vagrant/venv/bin/pip install -r /home/vagrant/projeto2/requirements.txt
    else
      echo "=== requirements.txt não encontrado. Instalando Flask e Gunicorn ==="
      sudo -u vagrant -H /home/vagrant/venv/bin/pip install --upgrade pip
      sudo -u vagrant -H /home/vagrant/venv/bin/pip install flask gunicorn
    fi

        # criar pasta de logs e garantir permissão
    mkdir -p /home/vagrant/projeto2/logs
    chown -R vagrant:vagrant /home/vagrant/projeto2

    # Criar systemd unit para gunicorn (assume app.py com app = Flask(...))
    cat > /etc/systemd/system/gunicorn-projeto2.service <<EOF
[Unit]
Description=Gunicorn instance for projeto2
After=network.target

[Service]
User=vagrant
Group=www-data
WorkingDirectory=/home/vagrant/projeto2
Environment="PATH=/home/vagrant/venv/bin"
# grava logs dentro da pasta do projeto para facilitar debug
ExecStart=/home/vagrant/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app \
  --access-logfile /home/vagrant/projeto2/logs/gunicorn_access.log \
  --error-logfile  /home/vagrant/projeto2/logs/gunicorn_error.log

Restart=always

[Install]
WantedBy=multi-user.target
EOF

    echo "=== Recarregando systemd e iniciando gunicorn ==="
    systemctl daemon-reload
    systemctl enable gunicorn-projeto2
    systemctl restart gunicorn-projeto2


    # Configurar Apache como reverse proxy
    APACHE_SITE=/etc/apache2/sites-available/projeto2.conf

    cat > $APACHE_SITE <<EOF
<VirtualHost *:80>
    ServerName projeto2

    # Proxy para gunicorn (aplicacao Python)
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    # Se tiver pasta de estáticos no Flask: /home/vagrant/projeto2/static
    Alias /static /home/vagrant/projeto2/static
    <Directory /home/vagrant/projeto2/static>
        Require all granted
        Options Indexes FollowSymLinks
    </Directory>

    ErrorLog \${APACHE_LOG_DIR}/projeto2_error.log
    CustomLog \${APACHE_LOG_DIR}/projeto2_access.log combined
</VirtualHost>
EOF

    a2ensite projeto2.conf
    a2dissite 000-default.conf || true

    echo "=== Reiniciando Apache ==="
    systemctl restart apache2

    echo "=== Provisionamento finalizado ==="
    echo "Acesse a aplicação em http://localhost:8080"
  SHELL
end
