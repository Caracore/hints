# 🍓 Installer Hints sur Raspberry Pi OS (PiOS)

> **Hints** permet de naviguer dans les applications graphiques Linux **sans souris**,
> en affichant des labels (hints) que vous tapez au clavier pour cliquer, scroller ou glisser.
>
> Ce guide explique pas à pas comment installer et configurer Hints sur un Raspberry Pi
> sous PiOS (Bookworm ou plus récent).

---

## 📋 Prérequis

| Élément | Détail |
|---------|--------|
| **Matériel** | Raspberry Pi 500+, Pi 5, ou Pi 4 (architecture ARM64/aarch64) |
| **Système** | Raspberry Pi OS **Bookworm** (Debian 12) ou plus récent |
| **Compositeur** | labwc (PiOS Trixie+), wayfire (PiOS Bookworm), ou X11/openbox |
| **Connexion internet** | Requise pour l'installation |

---

## 🚀 Étape 1 — Installation

Ouvrez un terminal et lancez le script d'installation :

```bash
curl -fsSL https://raw.githubusercontent.com/Caracore/hints/pios-support/install_pios.sh | bash
```

Ce script fait automatiquement :
1. Détecte votre modèle de Raspberry Pi
2. Installe les dépendances système (GTK, AT-SPI, Cairo, OpenCV, etc.)
3. Installe [UV](https://docs.astral.sh/uv/) temporairement
4. Installe Hints via UV
5. Nettoie les fichiers temporaires

> **Note :** Le script vous demandera votre mot de passe `sudo` pour installer les paquets système.

---

## ⚙️ Étape 2 — Configuration initiale (setup)

Cette étape configure l'accessibilité, le module uinput et le daemon hintsd.

```bash
sudo env XDG_SESSION_TYPE=$XDG_SESSION_TYPE \
     env XDG_CURRENT_DESKTOP=$XDG_CURRENT_DESKTOP \
     $(whereis hints | awk '{print $2}') --setup
```

Le script vous affichera les actions qu'il va effectuer et demandera confirmation.

**Ce qu'il fait :**
- ✅ Ajoute les variables d'accessibilité AT-SPI dans `/etc/environment`
- ✅ Charge le module `uinput` (nécessaire pour la souris virtuelle)
- ✅ Crée les règles udev et ajoute votre utilisateur au groupe `input`
- ✅ Active et démarre le daemon `hintsd` (service de souris virtuelle)

> ⚠️ **Quand le script propose de redémarrer, répondez `n` (non).**
> On va d'abord configurer le raccourci clavier avant de rebooter.

---

## ⌨️ Étape 3 — Raccourci clavier

### Si vous êtes sous labwc (PiOS Trixie+ / Bookworm récent)

Éditez le fichier `~/.config/labwc/rc.xml` :

```bash
nano ~/.config/labwc/rc.xml
```

Ajoutez les lignes suivantes **à l'intérieur** de la balise `<keyboard>`, juste avant `</keyboard>` :

```xml
    <keybind key="W-j">
      <action name="Execute" command="/home/VOTRE_UTILISATEUR/.local/bin/hints" />
    </keybind>
    <keybind key="W-k">
      <action name="Execute" command="/home/VOTRE_UTILISATEUR/.local/bin/hints -m scroll" />
    </keybind>
```

> 💡 Remplacez `VOTRE_UTILISATEUR` par votre nom d'utilisateur (ex: `linoux`).
> Pour trouver le chemin exact : `whereis hints`

Rechargez la configuration sans redémarrer :

```bash
labwc --reconfigure
```

### Si vous êtes sous wayfire (PiOS Bookworm par défaut)

Éditez le fichier `~/.config/wayfire.ini` :

```bash
nano ~/.config/wayfire.ini
```

Ajoutez sous la section `[command]` (créez-la si elle n'existe pas) :

```ini
[command]
binding_hints = <super> KEY_J
command_hints = /home/VOTRE_UTILISATEUR/.local/bin/hints

binding_hints_scroll = <super> KEY_K
command_hints_scroll = /home/VOTRE_UTILISATEUR/.local/bin/hints -m scroll
```

### Si vous êtes sous X11/openbox

Utilisez l'outil de raccourcis de votre environnement de bureau ou éditez
`~/.config/openbox/lxde-pi-rc.xml` pour ajouter un raccourci similaire.

---

## 🔄 Étape 4 — Redémarrage

Le redémarrage est **obligatoire** pour que les variables d'accessibilité soient
chargées par toutes les applications.

```bash
sudo reboot
```

---

## 🎮 Étape 5 — Utilisation

Après le redémarrage, ouvrez une application (navigateur, gestionnaire de fichiers, etc.)
puis appuyez sur :

### 🍓 + J — Mode Hints (clic)

> **🍓** = La touche **Raspberry Pi** (Super) en bas à gauche du clavier Pi 500.
> Sur un clavier externe, c'est la touche **Super** / **Windows** / **⌘**.

Des labels apparaissent sur les éléments cliquables. Tapez les lettres pour cliquer.

### Raccourcis disponibles

| Raccourci | Action |
|-----------|--------|
| <kbd>🍓</kbd> + <kbd>J</kbd> | Afficher les hints |
| Taper les lettres (ex: `jk`) | Cliquer sur l'élément |
| <kbd>2</kbd> puis les lettres | Clic multiple (double-clic, etc.) |
| <kbd>Shift</kbd> + lettres | Clic droit |
| <kbd>Alt</kbd> + lettres | Glisser-déposer (drag) |
| <kbd>Ctrl</kbd> + lettres | Survol (hover) |
| <kbd>🍓</kbd> + <kbd>K</kbd> | Mode scroll |
| <kbd>h</kbd> <kbd>j</kbd> <kbd>k</kbd> <kbd>l</kbd> | Scroller (gauche, bas, haut, droite) — style Vim |
| <kbd>Échap</kbd> | Quitter le mode hints / scroll |

---

## 🔧 Dépannage

### Hints ne se lance pas / pas de labels

1. Vérifiez que le daemon tourne :
   ```bash
   systemctl --user status hintsd
   ```
   S'il n'est pas actif :
   ```bash
   systemctl --user enable --now hintsd
   ```

2. Vérifiez les variables d'accessibilité :
   ```bash
   cat /etc/environment | grep ACCESSIBILITY
   ```
   Vous devez voir `ACCESSIBILITY_ENABLED=1`. Si ce n'est pas le cas, relancez le setup.

3. Avez-vous redémarré après le setup ? C'est indispensable.

### Erreur "Could not communicate with the hintsd service"

Le daemon `hintsd` n'est pas démarré :
```bash
systemctl --user start hintsd
```

### Écran noir / fenêtre opaque au lieu de transparente

Votre compositeur ne supporte pas la transparence correctement.
Vérifiez que vous êtes bien sous labwc ou wayfire (Wayland), pas sous un
environnement X11 sans compositeur.

### Hints bloqué / clavier ne répond plus

Basculez sur un terminal virtuel avec <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>F2</kbd>,
connectez-vous, puis :
```bash
killall hints
```
Revenez avec <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>F1</kbd>.

---

## 📁 Fichiers importants

| Fichier | Description |
|---------|-------------|
| `~/.local/bin/hints` | Exécutable principal |
| `~/.local/bin/hintsd` | Daemon de souris virtuelle |
| `~/.config/hints/config.json` | Configuration de Hints (alphabet, couleurs, etc.) |
| `~/.config/labwc/rc.xml` | Raccourcis clavier labwc |
| `~/.config/wayfire.ini` | Raccourcis clavier wayfire |
| `/etc/environment` | Variables d'accessibilité AT-SPI |
| `~/.config/systemd/user/hintsd.service` | Service systemd du daemon |

---

## 🗑️ Désinstallation

```bash
# Supprimer hints
uv tool uninstall hints

# Désactiver le daemon
systemctl --user disable --now hintsd
rm ~/.config/systemd/user/hintsd.service

# Retirer les raccourcis clavier de votre rc.xml ou wayfire.ini
```

---

## 📚 Pour aller plus loin

- [Wiki Hints](https://github.com/AlfredoSequeida/hints/wiki) — Configuration avancée, règles par application
- [Dépôt original](https://github.com/AlfredoSequeida/hints) — Code source et issues
