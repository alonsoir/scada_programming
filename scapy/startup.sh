# Configurar sistema completo
sudo bash production_setup.sh

# Iniciar como servicio
sudo systemctl start unusual-protocol-detector  # Linux
# o
sudo launchctl load /Library/LaunchDaemons/com.security.unusual-protocol-detector.plist  # macOS