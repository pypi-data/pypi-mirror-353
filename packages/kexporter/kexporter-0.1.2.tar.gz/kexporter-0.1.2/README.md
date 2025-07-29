# kexporter

> 🧾 Exportateur de salons ou fils Discord au format HTML, avec rendu fidèle à l'interface Discord.  

![PyPI](https://img.shields.io/pypi/v/kexporter?style=flat-square&color=0a7cdb)
![Code Usage](https://img.shields.io/badge/code%20used-90%%25-0a7cdb?style=flat-square)
![GitHub stars](https://img.shields.io/github/stars/itsKushh/kexporter?style=flat-square&color=0a7cdb)
![GitHub forks](https://img.shields.io/github/forks/itsKushh/kexporter?style=flat-square&color=0a7cdb)
![Downloads](https://img.shields.io/pypi/dt/kexporter?style=flat-square&color=0a7cdb)
![License](https://img.shields.io/badge/license-GPL--3.0-0a7cdb?style=flat-square)
![Issues](https://img.shields.io/github/issues/itsKushh/kexporter?style=flat-square&color=0a7cdb)

---

## 💙 À propos

`kexporter` est un module Python qui permet d’exporter des messages de salons Discord vers un fichier HTML statique, visuellement proche de l’interface réelle de Discord, retravaillé à ma vision.

Il est utile pour :
- archiver des conversations importantes ;
- créer des rapports client / ticket ;
- documenter des échanges dans un format lisible hors ligne.

---

## 📦 Installation

**PyPI:**

```bash
pip install kexporter
```

---

## ⚙️ Utilisation

```python
from kexporter import export

# Exemple fictif / Example usage
await export(channel, output_path="transcript.html")
```

⚠️ Ton bot Discord doit avoir la permission de lire l'historique.  

---

## ✅ Fonctionnalités

- ✅ Export HTML statique
- 🖼️ Avatars et pseudos
- 🕒 Horodatage des messages
- 🎨 Rendu fidèle à Discord
- 📎 Pièces jointes supportées (optionnel)
- 🔧 Facilement intégrable

---

## 🖼️ Aperçu

*ça arrive bientôt...*  
`transcript.html`

---

## 🔧 Dépendances

- `discord.py >= 2.5.2`
- `jinja2 >= 3.1.6`

---

## 📄 Licence

**GPL v3.0 - Licence libre avec obligation de partage à l’identique**  

> Ce logiciel est distribué sous la licence GNU GPL v3. Toute redistribution, modification ou intégration dans un autre projet **doit mentionner l’auteur original** et conserver la même licence (GPL v3 ou compatible).  

🔗 [Texte complet de la licence](https://www.gnu.org/licenses/gpl-3.0.fr.html)

---

## 🙋‍♂️ Auteur

Développé par [Kushh](https://github.com/itsKushh)  

Contact : @kushh

---

## 💡 Contribuer

Les pull requests sont bienvenues ! Forkez le projet et proposez vos idées.  
