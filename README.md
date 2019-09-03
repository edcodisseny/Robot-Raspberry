# Robot-Raspberry

Copiar robotController.py al mateix directori del programa.

## Configuració WiFi sense pantalla
Per a aquest procés, necessitarem connectar la targeta micro-sd al nostre ordinador.
1. Anar a /boot de la SD i afegir un arxiu amb el nom ssh (sense extensió i sense contingut)
2. Modificar l'arxiu /etc/wpa_supplicant/wpa_supplicant.conf, deixant-ho amb el següent contingut:

```
 ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev 
 update_config=1
 network={
  ssid="nombre de tu router o SSID"
  psk="tu contraseña del wi-fi"
  key_mgmt=WPA-PSK 
 } 
```

## Mostrar IP automàticament
### Crontab
Creem un arxiu executable (donar-li permisos chmod 777) com start.sh, amb les següents línies:

```
 #!/bin/bash
 python3 /home/pi/lcdIP.py
```

Executem al terminal:

<code>
 crontab -e
</code>

Que ens permetrà editar els arxius que s'executen a l'inici. Afegim al final del document la línia:

<code>
 @reboot /home/pi/start.sh
</code>

Cada vegada que arrenquem el sistema operatiu executarà aquest fitxer.
