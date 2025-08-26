# Système de Traduction Multilingue BIMEX

## Vue d'ensemble

Le système de traduction multilingue BIMEX permet d'afficher vos pages web en français, anglais et allemand selon la préférence de l'utilisateur. Il utilise des boutons avec des drapeaux pour une interface intuitive et moderne.

## Fonctionnalités

- 🌍 **3 langues supportées** : Français (FR), Anglais (EN), Allemand (DE)
- 🎯 **Interface intuitive** : Boutons avec drapeaux nationaux
- 💾 **Persistance** : La langue choisie est sauvegardée dans le navigateur
- ⚡ **Temps réel** : Changement de langue instantané sans rechargement
- 🎨 **Design cohérent** : Style futuriste BIMEX avec effets néon

## Fichiers inclus

### 1. `translations.js`
Fichier principal contenant toutes les traductions et la logique de changement de langue.

### 2. Composant de sélecteur de langue
Interface utilisateur avec 3 boutons de drapeaux (FR, EN, DE).

### 3. Pages modifiées
- `bim_analysis.html` - Interface d'analyse BIM
- `report_template.html` - Modèle de rapport
- `home.html` - Page d'accueil BIM
- `accueil.html` - Page d'accueil principale

### 4. Page de démonstration
`demo_translation.html` - Page de test du système de traduction

## Comment l'utiliser

### 1. Intégration dans une nouvelle page

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <!-- Inclure le fichier de traductions -->
    <script src="translations.js"></script>
    <title data-translate="page_title">Titre de la page</title>
</head>
<body>
    <!-- Ajouter le sélecteur de langue -->
    <div class="language-selector">
        <div class="lang-buttons">
            <button class="lang-btn" data-lang="fr" title="Français">
                <img src="..." alt="🇫🇷 Français">
                <span>FR</span>
            </button>
            <!-- Boutons EN et DE similaires -->
        </div>
    </div>
    
    <!-- Contenu avec attributs de traduction -->
    <h1 data-translate="page_title">Titre de la page</h1>
    <p data-translate="description">Description de la page</p>
</body>
</html>
```

### 2. Ajouter des traductions

Dans `translations.js`, ajoutez vos clés de traduction :

```javascript
const translations = {
    fr: {
        "page_title": "Titre en français",
        "description": "Description en français"
    },
    en: {
        "page_title": "Title in English",
        "description": "Description in English"
    },
    de: {
        "page_title": "Titel auf Deutsch",
        "description": "Beschreibung auf Deutsch"
    }
};
```

### 3. Attributs de traduction

- `data-translate="clé"` : Pour le contenu textuel
- `data-translate-placeholder="clé"` : Pour les placeholders des champs

## Styles CSS

Le système inclut des styles CSS complets pour le sélecteur de langue :

```css
.language-selector {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    background: rgba(26, 26, 46, 0.9);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 245, 255, 0.3);
    border-radius: 12px;
    padding: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

## Fonctions JavaScript

### `changeLanguage(lang)`
Change la langue de l'interface et sauvegarde le choix.

### `updateInterface(lang)`
Met à jour tous les éléments traduits de la page.

### `initLanguage()`
Initialise la langue au chargement de la page.

## Personnalisation

### Changer les couleurs
Modifiez les variables CSS dans `:root` :

```css
:root {
    --primary-neon: #00f5ff;    /* Couleur principale */
    --secondary-neon: #ff0080;  /* Couleur secondaire */
    --bg-dark: #0a0a0f;        /* Arrière-plan sombre */
}
```

### Changer la position
Modifiez les propriétés CSS du sélecteur :

```css
.language-selector {
    top: 20px;      /* Distance du haut */
    right: 20px;    /* Distance de la droite */
    /* ou left: 20px; pour le côté gauche */
}
```

### Ajouter des langues
1. Ajoutez un nouveau bouton dans le HTML
2. Ajoutez les traductions dans `translations.js`
3. Ajoutez le drapeau correspondant

## Compatibilité

- ✅ Tous les navigateurs modernes
- ✅ Responsive design
- ✅ Accessibilité (titres et alt text)
- ✅ Performance optimisée

## Support

Pour toute question ou problème avec le système de traduction, consultez :
- Le fichier `demo_translation.html` pour des exemples
- Les commentaires dans `translations.js`
- La documentation des attributs HTML5

## Licence

Ce système de traduction fait partie du projet BIMEX et suit les mêmes conditions d'utilisation.


