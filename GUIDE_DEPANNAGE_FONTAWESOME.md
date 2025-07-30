# 🔧 Guide de Dépannage - Erreur FontAwesome

## 🚨 Problème
```
GET http://localhost:8000/lib/fontawesome-free-5.11.2-web/css/all.min.css 404 (Not Found)
```

## 🔍 Cause du Problème
L'erreur se produit quand le viewer XeoKit est accédé via le **mauvais port** :
- ❌ **Port 8000** : Backend Python (FastAPI) - ne sert pas les fichiers statiques du viewer
- ✅ **Port 8081** : Frontend HTTP Server - sert correctement tous les fichiers statiques

## ✅ Solutions

### **Solution 1 : Utiliser le Bon Port (Recommandée)**

1. **Démarrer le serveur frontend :**
   ```bash
   npx http-server . -p 8081
   ```

2. **Accéder au viewer via le bon port :**
   ```
   http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=basic2
   ```

3. **Utiliser la page d'accueil :**
   ```
   http://localhost:8081/xeokit-bim-viewer/app/home.html
   ```

### **Solution 2 : Script de Démarrage Automatique**

Utilisez le script `start_servers.bat` qui démarre automatiquement les deux serveurs :
```bash
start_servers.bat
```

### **Solution 3 : Vérification des URLs**

| Service | Port | URL Correcte |
|---------|------|--------------|
| 🏠 Page d'accueil | 8081 | `http://localhost:8081/xeokit-bim-viewer/app/home.html` |
| 👁️ Viewer 3D | 8081 | `http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=PROJECT_ID` |
| 🔧 API Backend | 8000 | `http://localhost:8000/docs` |
| 📊 Analyse BIM | 8000 | `http://localhost:8000/analysis?project=PROJECT_ID&auto=true` |

## 🔧 Corrections Appliquées

### **1. Balise Base dans index.html**
```html
<base href="http://localhost:8081/xeokit-bim-viewer/app/">
```

### **2. CDN FontAwesome de Fallback**
```html
<link rel="stylesheet" href="./lib/fontawesome-free-5.11.2-web/css/all.min.css" type="text/css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/all.min.css" type="text/css" onerror="this.remove()" />
```

### **3. Correction du Lien dans home.html**
```javascript
function viewModel(projectId) {
    const viewerUrl = `http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=${projectId}`;
    window.open(viewerUrl, '_blank');
}
```

## 🧪 Tests de Validation

### **Test 1 : Ressources Accessibles**
```bash
cd backend
python test_viewer_resources.py
```

**Résultat attendu :** ✅ TOUTES LES RESSOURCES SONT ACCESSIBLES!

### **Test 2 : Viewer Fonctionnel**
1. Ouvrir : `http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=basic2`
2. Vérifier : Pas d'erreur 404 dans la console
3. Confirmer : Modèle 3D se charge correctement

## 🚨 Erreurs Communes et Solutions

### **Erreur : "address already in use 0.0.0.0:8000"**
**Cause :** Le backend Python est déjà en cours d'exécution
**Solution :** 
```bash
# Arrêter le processus existant ou utiliser un autre port
python backend/main.py --port 8001
```

### **Erreur : "Cannot GET /xeokit-bim-viewer/app/index.html"**
**Cause :** Serveur http-server non démarré sur port 8081
**Solution :**
```bash
npx http-server . -p 8081
```

### **Erreur : FontAwesome ne s'affiche pas**
**Cause :** Fichiers de polices manquants
**Solution :** Le CDN de fallback devrait résoudre le problème automatiquement

## 📋 Checklist de Dépannage

- [ ] Serveur http-server démarré sur port 8081
- [ ] Backend Python démarré sur port 8000
- [ ] Accès au viewer via port 8081 (pas 8000)
- [ ] Fichier `xeokit-bim-viewer.es.js` présent dans `dist/`
- [ ] Balise `<base>` correcte dans `index.html`
- [ ] Projet existe dans `xeokit-bim-viewer/app/data/projects/`

## 🎯 URLs de Test Finales

Une fois les serveurs démarrés correctement :

1. **Page d'accueil :** http://localhost:8081/xeokit-bim-viewer/app/home.html
2. **Viewer avec basic2 :** http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=basic2
3. **Analyse BIM :** http://localhost:8000/analysis?project=basic2&auto=true&file_detected=true

## ✅ Statut Final

- 🎉 **Fichier xeokit-bim-viewer.es.js recréé**
- 🎯 **Erreurs FontAwesome corrigées**
- 🚀 **Viewer XeoKit entièrement fonctionnel**
- 📋 **Documentation complète disponible**
