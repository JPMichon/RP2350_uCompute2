# :computer: RP2350 uCompute2

## [English version available here](./README.EN.md)


Le **RP2350 uCompute2** est une plateforme de développement embarquée, autonome et hautement modulaire basée sur le microcontrôleur **Raspberry Pi Pico RP2350**. Conçue comme une solution matérielle tout-en-un, elle intègre un stockage étendu, des interfaces d'affichage polyvalentes ainsi qu'un écosystème de cartes filles interchangeables (Ethernet, WiFi, Radio, VGA), la rendant idéale pour les projets embarqués complexes, le prototypage réseau et l'apprentissage.

La carte offre une double approche logicielle : elle peut être programmée et utilisée exactement comme un Raspberry Pi Pico classique, ou utiliser le GUI (uComputeOS) conçu pour cette plateforme. Ce mini-système d'exploitation écrit en MicroPython offre une interface graphique interactive pour explorer, copier et exécuter dynamiquement des scripts stockés dans la mémoire QFlash ou sur la carte Micro SD.

>[!NOTE]
>Pour les plus perspicaces, le **RP2350 uCompute2** est une évolution de mon projet **[RP2040 uCompute](https://github.com/JPMichon/RP2040_uCompute)**. Ces deux projets partagent le même ADN ; les modules sont donc compatibles entre eux et règle générale, le code en **MicroPython** est compatible entre les deux systèmes. Puisque le microcontrôleur est différent, il va de soi que vous ne pouvez pas utiliser le firmware compilé pour le **RP2040** , car il ne tournera pas sur >le **RP2350**.
<br>

<img width="703" height="314" alt="image" src="https://github.com/user-attachments/assets/fe666037-9144-4d45-a901-445b3db0c9fb" />

_Dimensions: 96mm x 42mm_ <BR>

---

# 🤖 Assistants de Codage IA

Si vous utilisez un agent IA (comme ChatGPT, Claude ou GitHub Copilot) pour vous aider à développer sur la RP2350 uCompute2, configurez-le instantanément en lui copiant-collant l'un de nos profils personnalisés. L'IA connaîtra immédiatement toutes les définitions de broches et les adresses exactes de la carte pour coder sans faire d'erreurs matérielles !

💼 **[Mode Développeur Freelance de uCompute](RP2040_UCompute_FreelanceCoder.md)** Conçu pour l'efficacité et la vitesse. L'IA se comporte comme un programmeur senior à votre service : vous lui exposez votre concept ou votre cahier des charges, et elle vous livre un script complet, optimisé et immédiatement prêt à être copié-collé.

---

## 🛠️ Spécifications Techniques & Dimensions

- RP2350 
- LCD 1.3" 240x240 IPS ST7789
- EEPROM I2C `CAT24Cxx` (optionel)
- Bornier pour néopixel
- 1 Connecteur JST pour des modules I2C
- 3 boutons pour l'interface utilisateur (relié ADC0)
- SIP pour prototypage (10 IOs).
- Port USB (USB Mini-B ou USB-C) selon la version.
- Fusible PTC (500ma)
- Piezo
- Lecteur MicroSD
- QSPI flash en boitier SOP8 permettant de choisir la taille (2meg - 16meg)
- DEL connecté au port standard GP25
- support pour un module Ethernet W5500
- Trous de montage 3mm
- Dimensions: 96mm x 42mm
<BR>

---

### Le bornier IOs (1x14 Pins Header):
Le bornier (pins Header) facilite le prototypage. l'espacement est standard a 2,54 mm ceci permet de l'enficher dans un carte de prototypage (Protoboard) ou des cables de liaison (jumper wires) avec embouts *Dupont* afin de relier vos circuits ou modules.

### Alimentation & Signaux:
1. **5V** (Alimentation directe issue de l'USB, idéale pour la puissance)
2. **3.3V** (Régulée via l'AP2114H-3.3TRG1)
3. **GND** (Masse commune)
4. **UART 0** : `GP0` (TX) & `GP1` (RX)
5. **2 Entrées Analogiques (ADC) :** `GP27` (ADC1) & `GP28` (ADC2)
6. **6 Broches Numériques (GPIO) :** `GP16`, `GP17`, `GP18`, `GP19`, `GP22`, `GP24`
<BR>

> [!CAUTION]
> **Le RP2350 est tolérant au 5V. MAIS...** 
> Le rail d'alimentation IOVDD doit impérativement être sous tension (à 3.3V) dès qu'un signal 5V est appliqué sur une broche GPIO. Si un signal **5V** est envoyé dans une broche alors que l'IOVDD du RP2350 est éteint ou relié à la masse, la broche subira des dommages électriques irréversibles.<BR>
> **Les broches analogiques ne tolèrent PAS le 5V**
La tolérance au **5V** s'applique uniquement aux broches GPIO purement numériques. Les broches qui partagent leur fonction avec les entrées analogiques du convertisseur (les canaux ADC) ne possèdent pas cette protection et seront détruites si elles sont exposées à du **5V**.<BR>

## 🔌 Alimentation Alternative en 5v

La façon la plus usuelle est d'alimenter le circuit via le connecteur USB. Néanmoins, il est possible d'alimenter le circuit en **5V** à partir de la **broche 1** du connecteur Neopixel ou via la **pin 1** du bornier d'extension. La diode **D1** protège le port USB du retour de courant, mais il est toujours préférable de couper l'alimentation **5V** externe si vous raccordez le circuit à un ordinateur.

> [!WARNING]
> Le Vin absolu du régulateur AP2114H-3.3TRG1 est de 6.5v, donc **max 5,5v**.

---

## Assignation des IOs

```Python
_MicroSD_Detect = 7 # détection de la présence d'une carte MicroSD (GP7)
_MicroSD_Select = 13 # définition de la pin Select du SDCARD (GP13)
_W5500_Select = 8 # définition de la pin Select du W5500 (GP8)
_W5500_Reset = 10 # définition de la pin Reset du W5500 (GP10)
_SPI1_SCK = 14 # SPI1_shared Clock
_SPI1_MOSI = 15 # SPI1_shared MOSI
_SPI1_MISO = 12 # SPI1_shared MISO
_ST7789_SCK = 2 # définition de la pin Clock du ST7789 (GP2) SPI0
_ST7789_MOSI = 3 # définition de la pin MOSI du ST7789 (GP3) SPI0
_ST7789_RESET = 4 # définition de la pin Reset du ST7789 (GP4)
_ST7789_DC = 5 # définition de la pinSelect du ST7789 (GP5)
_ST7789_BL = 6 # définition de la pinBacklit du ST7789 (GP6)
_Led_System = 25 # définition du port  del systeme (GP25)
_I2C_SDA = 20 # définition de Data du I2C(0) (GP20)
_I2C_SCL = 21 # définition de SCL du I2C(0) (GP21)
_Buzzer = 11 # définition du  buzzer (GP11)
_NeoPixel = 23 # définition du port NeoPixel (GP23)
_EEPROM_ADDR = 0x50 # adresse du eeprom
_Boutons = 26 # définition du port analogue des boutons (GP26)
_UART = 0 # UART par defaut
_TX_PIN = 0 # TX Pin (GP0)
_RX_PIN = 1 # TX Pin (GP1)
```
---

## 🔌 Écosystème de Modules d'Extension (Add-ons)

Le socket arrière double rangée et le connecteur d'affichage avant forment un port d'extension standardisé permettant d'adapter le matériel à l'application visée.

### 1. Modules de Communication (Socket Arrière)
L'empreinte mécanique et électrique est compatible avec plusieurs technologies interchangeables :

<img width="221" height="288" alt="image" src="https://github.com/user-attachments/assets/b017c095-deda-49ad-ae25-3661ce4e3009" /><br>
* **Module Ethernet (W5500) :** Apporte une connectivité réseau filaire stable en SPI. (requiert un firmware spécial)
* **Module WiFi (ESP-12F) :** Carte d'adaptation embarquant un module ESP8266 pour ajouter une connectivité Wi-Fi.
*  <img width="203" height="266" alt="image" src="https://github.com/user-attachments/assets/f0c80621-1b07-46e6-844b-4594e3d338f9" /><br>
* **Module Radio (NRF24L01 - GT-24 Mini.MK1) :** Adaptateur doté d'un connecteur 2x4 broches femelle pour liaisons radio point à point (2.4 GHz) à basse consommation.<br>
<img width="226" height="277" alt="image" src="https://github.com/user-attachments/assets/a6a0a83b-80ed-4dbc-bc28-06579f64b54c" />

---

### 2. Module d'Affichage & Vidéo (Socket Avant)
* **µCompute VGA8 Adaptor (REV 1.0) :** Se connecte à la place de l'écran LCD ST7789 pour générer et exporter un signal vidéo analogique vers un moniteur standard via un port **VGA (DE-15)**. 

<img width="343" height="292" alt="image" src="https://github.com/user-attachments/assets/a070a613-6fbb-4731-9103-bb9ae0ae5e83" />

---

## 🎓 Accessibilité & Compatibilité avec le Raspberry Pi Pico

Si vous débutez en programmation ou en électronique, ne soyez pas intimidés ! Bien que la **RP2350 uCompute2** intègre de nombreux composants sur un seul circuit imprimé (VGA, Wi-Fi, MicroSD, etc.), **son cœur reste un Raspberry Pi Pico 2 standard**. 

Il y a en réalité **très peu de différences** fondamentales entre cette carte et un Pi Pico classique :
* **Même puce :** Le microcontrôleur principal est le RP2350. Tout code écrit pour un Pico standard fonctionnera ici.
* **Mêmes bases :** La logique de programmation, l'utilisation des broches (GPIO) et l'environnement restent identiques.

### 📚 Ressources pour les débutants

Puisque l'architecture est la même, vous pouvez utiliser à 100 % les guides, tutoriels et documentations officiels de la fondation Raspberry Pi pour apprendre à programmer votre **RP2350 uCompute2**. 

Pour faire vos premiers pas, je vous recommande vivement le guide officiel : <br>
👉 **[Getting started with the Raspberry Pi Pico (Raspberry Pi Projects)](https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico)**

Ce guide vous apprendra pas à pas à :
1. Installer et configurer l'environnement de développement **Thonny**.
2. Connecter votre carte à votre ordinateur et y installer le micrologiciel **MicroPython**.
3. Écrire vos premiers scripts pour contrôler des entrées et des sorties.

Une fois que vous aurez compris les bases du clignotement d'une LED ou de la lecture d'un bouton avec ce guide, l'écosystème de la **RP2350 uCompute2** et ses scripts de test (`testcode/`) vous permettront d'aller beaucoup plus loin (affichage graphique, son, jeux et réseau) sans changer de méthode de travail !
<BR>

---
## 💾 Partie Logicielle : uComputeOS

La carte exécute **uComputeOS**, un mini-système d'exploitation embarqué écrit en MicroPython. 

### Dépendances matérielles à inclure (dossier `lib/`) :
* **Version Écran LCD :** `st7789py.py`, `framebuf2.py`, `vga1_8x8.py`, `vga2_bold_16x16.py`
* **Stockage commun :** `sdcard.py`

### Caractéristiques majeures de uComputeOS :
1. **Écran de démarrage (Splash Screen) :** Affiche les informations systèmes (`os.uname`), la version du firmware ainsi que l'espace Flash total et libre calculé en direct.
2. **Gestionnaire de fichiers (FileManager) :** Détecte dynamiquement à l'allumage si une carte Micro SD est présente. L'utilisateur sélectionne son espace de stockage racine (`FLASH` ou `SD`).
3. **Navigation & Sélection :** Interface visuelle navigable à l'aide du bouton analogique (`Up`, `Down`, `Select`). Un curseur en forme de triangle pointe vers le script sélectionné.
4. **Exécution dynamique (`EXEC`) :** Permet d'ouvrir n'importe quel fichier `.py` utilisateur présent sur le support et de l'exécuter à la volée. En cas d'erreur de code, uComputeOS capture l'exception et affiche un écran d'erreur rouge sans faire planter la carte.
5. **Copie Inter-Stockage (`CP>SD` / `CP>\`) :** Intègre une fonction de copie par blocs (512 octets) permettant de transférer un script de la mémoire Flash interne vers la carte SD (et inversement) directement depuis l'interface matérielle.

### ⚙️ Exécution automatique au démarrage (Configuration en `main.py`)

Pour que l'interface graphique (**uComputeOS**) se lance automatiquement dès la mise sous tension de la carte sans nécessiter d'ordinateur, vous devez l'enregistrer comme script principal :

1. **Renommez le fichier** choisi en **`main.py`**.
2. **Transférez-le à la racine** de la mémoire Flash interne du RP2350 (et non dans le dossier `lib/`) à l'aide de votre IDE (comme Thonny).
3. **Assurez-vous** que toutes les dépendances requises (`sdcard.py`, pilotes d'écran et polices de caractères) sont bien présentes dans le dossier `/lib` de la mémoire interne. 

Au prochain redémarrage ou cycle d'alimentation, le micrologiciel MicroPython cherchera nativement le fichier `main.py` et propulsera instantanément la GUI à l'écran.

---

## 📜 Licence

Le matériel (fichiers de conception, schémas, typons) et les logiciels de ce projet sont mis à disposition selon les termes de la Licence **Creative Commons Attribution - Pas d'Utilisation Commerciale - Partage dans les Mêmes Conditions 4.0 International (CC BY-NC-SA 4.0)**.

❌ **L'utilisation commerciale de ce projet (revente de PCBs nus, kits ou cartes retroPico assemblées) est strictement interdite sans autorisation préalable de l'auteur.**

Consultez le fichier [LICENSE](LICENSE) pour lire l'intégralité des termes.

---

## ☕ Soutenir le projet

Si vous appréciez mon travail et souhaitez m'offrir un café pour me soutenir bénévolement dans mes futurs projets de soudure et de code, vous pouvez me laisser un pourboire sur Ko-fi. C'est entièrement volontaire et grandement apprécié !
