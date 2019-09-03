# Robot-Raspberry

Copiar robotController.py al mateix directori del programa.

## Mostrar IP automàticament
### Crontab
Creem un arxiu executable (donar-li permisos chmod 777) com start.sh, amb les següents línies:

<code>
 #!/bin/bash
 python3 /home/pi/lcdIP.py
</code>

Executem al terminal:

<code>
 crontab -e
</code>

Que ens permetrà editar els arxius que s'executen a l'inici. Afegim al final del document la línia:

<code>
 @reboot /home/pi/start.sh
</code>

Cada vegada que arrenquem el sistema operatiu executarà aquest fitxer.
