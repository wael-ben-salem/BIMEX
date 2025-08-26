// translation-rapport.js - Traductions pour les pages de rapport et d'accueil
const translations = {
    fr: {
        // Titres principaux
        "report_title": "BIMEX - Rapport d'Analyse BIM Avancée",
        "home_title": "BIMEX - Centre de Contrôle de Mission",
        "accueil_title": "BIMEX - Centre de Contrôle de Mission",
        
        // En-têtes et sous-titres
        "mission_control_center": "CENTRE DE CONTRÔLE DE MISSION",
        "intelligence_artificielle": "Intelligence Artificielle",
        "analyse_avancee": "Analyse Avancée",
        "rapport_analyse_bim": "🏗️ RAPPORT D'ANALYSE BIM AVANCÉE",
        
        // Navigation et boutons
        "retour": "Retour",
        "accueil": "Accueil",
        "telecharger": "Télécharger",
        "imprimer": "Imprimer",
        "partager": "Partager",
        "fermer": "Fermer",
        "suivant": "Suivant",
        "precedent": "Précédent",
        "valider": "Valider",
        "annuler": "Annuler",
        "sauvegarder": "Sauvegarder",
        
        // Actions et états
        "demarrer": "Démarrer",
        "arreter": "Arrêter",
        "pause": "Pause",
        "reprendre": "Reprendre",
        "actualiser": "Actualiser",
        "reinitialiser": "Réinitialiser",
        "configurer": "Configurer",
        "analyser": "Analyser",
        "generer": "Générer",
        
        // Statuts et messages
        "en_cours": "En cours",
        "termine": "Terminé",
        "en_attente": "En attente",
        "erreur": "Erreur",
        "succes": "Succès",
        "attention": "Attention",
        "information": "Information",
        "chargement": "Chargement...",
        "traitement": "Traitement en cours...",
        
        // Sections de rapport
        "resume_executif": "Résumé Exécutif",
        "analyse_detaillee": "Analyse Détaillée",
        "recommandations": "Recommandations",
        "conclusion": "Conclusion",
        "annexes": "Annexes",
        "methodologie": "Méthodologie",
        "resultats": "Résultats",
        "discussion": "Discussion",
        
        // Métriques et indicateurs
        "qualite_globale": "Qualité Globale",
        "score_performance": "Score de Performance",
        "niveau_conformite": "Niveau de Conformité",
        "efficacite": "Efficacité",
        "durabilite": "Durabilité",
        "cout_estime": "Coût Estimé",
        "delai_estime": "Délai Estimé",
        "risques": "Risques",
        "opportunites": "Opportunités",
        
        // Éléments BIM
        "elements_bim": "Éléments BIM",
        "modeles_3d": "Modèles 3D",
        "plans_2d": "Plans 2D",
        "donnees_techniques": "Données Techniques",
        "specifications": "Spécifications",
        "calculs": "Calculs",
        "simulations": "Simulations",
        
        // Interface utilisateur
        "tableau_bord": "Tableau de Bord",
        "menu_principal": "Menu Principal",
        "recherche": "Recherche",
        "filtres": "Filtres",
        "tri": "Tri",
        "affichage": "Affichage",
        "preferences": "Préférences",
        "aide": "Aide",
        "support": "Support",
        
        // Messages système
        "connexion_reussie": "Connexion réussie",
        "deconnexion": "Déconnexion",
        "session_expiree": "Session expirée",
        "acces_refuse": "Accès refusé",
        "fichier_introuvable": "Fichier introuvable",
        "operation_reussie": "Opération réussie",
        "operation_echouee": "Opération échouée",
        
        // Temps et dates
        "aujourd_hui": "Aujourd'hui",
        "hier": "Hier",
        "cette_semaine": "Cette semaine",
        "ce_mois": "Ce mois",
        "cette_annee": "Cette année",
        "derniere_mise_a_jour": "Dernière mise à jour",
        "date_creation": "Date de création",
        "date_modification": "Date de modification",
        
        // Formats et unités
        "pourcentage": "Pourcentage",
        "nombre": "Nombre",
        "texte": "Texte",
        "date": "Date",
        "heure": "Heure",
        "taille": "Taille",
        "poids": "Poids",
        "volume": "Volume",
        
        // Notifications
        "nouveau_message": "Nouveau message",
        "mise_a_jour_disponible": "Mise à jour disponible",
        "synchronisation_terminee": "Synchronisation terminée",
        "sauvegarde_automatique": "Sauvegarde automatique",
        "connexion_perdue": "Connexion perdue",
        "reconnexion": "Reconnexion...",
        
        // Erreurs et avertissements
        "erreur_connexion": "Erreur de connexion",
        "erreur_chargement": "Erreur de chargement",
        "erreur_sauvegarde": "Erreur de sauvegarde",
        "donnees_incompletes": "Données incomplètes",
        "format_non_supporte": "Format non supporté",
        "taille_fichier_excessive": "Taille de fichier excessive",
        
        // Confirmation et validation
        "confirmer_action": "Confirmer l'action",
        "action_irreversible": "Cette action est irréversible",
        "supprimer_definitivement": "Supprimer définitivement ?",
        "modifications_non_sauvegardees": "Modifications non sauvegardées",
        "voulez_vous_continuer": "Voulez-vous continuer ?",
        "operation_annulee": "Opération annulée",
        
        // Informations utilisateur
        "profil_utilisateur": "Profil utilisateur",
        "parametres_compte": "Paramètres du compte",
        "securite": "Sécurité",
        "notifications": "Notifications",
        "langue": "Langue",
        "theme": "Thème",
        "accessibilite": "Accessibilité",
        
        // Fonctionnalités avancées
        "mode_avance": "Mode avancé",
        "mode_simple": "Mode simple",
        "personnalisation": "Personnalisation",
        "automatisation": "Automatisation",
        "intelligence_artificielle": "Intelligence Artificielle",
        "machine_learning": "Machine Learning",
        "analyse_predictive": "Analyse Prédictive",
        
        // Nouvelles clés ajoutées
        "scores_bimex": "Scores BIMEX",
        "system_operational": "SYSTÈME OPÉRATIONNEL",
        "ai_connected": "IA CONNECTÉE",
        "projects": "Projets",
        "new_generation": "Nouvelle Génération",
        "add_bim_model": "Ajouter un modèle BIM (IFC/RVT)",
        "search_project": "Rechercher un projet...",
        "loading_projects": "Chargement des projets..."
    },
    
    en: {
        // Main titles
        "report_title": "BIMEX - Advanced BIM Analysis Report",
        "home_title": "BIMEX - Mission Control Center",
        "accueil_title": "BIMEX - Mission Control Center",
        
        // Headers and subtitles
        "mission_control_center": "MISSION CONTROL CENTER",
        "intelligence_artificielle": "Artificial Intelligence",
        "analyse_avancee": "Advanced Analysis",
        "rapport_analyse_bim": "🏗️ ADVANCED BIM ANALYSIS REPORT",
        
        // Navigation and buttons
        "retour": "Back",
        "accueil": "Home",
        "telecharger": "Download",
        "imprimer": "Print",
        "partager": "Share",
        "fermer": "Close",
        "suivant": "Next",
        "precedent": "Previous",
        "valider": "Validate",
        "annuler": "Cancel",
        "sauvegarder": "Save",
        
        // Actions and states
        "demarrer": "Start",
        "arreter": "Stop",
        "pause": "Pause",
        "reprendre": "Resume",
        "actualiser": "Refresh",
        "reinitialiser": "Reset",
        "configurer": "Configure",
        "analyser": "Analyze",
        "generer": "Generate",
        
        // Status and messages
        "en_cours": "In Progress",
        "termine": "Completed",
        "en_attente": "Pending",
        "erreur": "Error",
        "succes": "Success",
        "attention": "Warning",
        "information": "Information",
        "chargement": "Loading...",
        "traitement": "Processing...",
        
        // Report sections
        "resume_executif": "Executive Summary",
        "analyse_detaillee": "Detailed Analysis",
        "recommandations": "Recommendations",
        "conclusion": "Conclusion",
        "annexes": "Appendices",
        "methodologie": "Methodology",
        "resultats": "Results",
        "discussion": "Discussion",
        
        // Metrics and indicators
        "qualite_globale": "Overall Quality",
        "score_performance": "Performance Score",
        "niveau_conformite": "Compliance Level",
        "efficacite": "Efficiency",
        "durabilite": "Sustainability",
        "cout_estime": "Estimated Cost",
        "delai_estime": "Estimated Time",
        "risques": "Risks",
        "opportunites": "Opportunities",
        
        // BIM elements
        "elements_bim": "BIM Elements",
        "modeles_3d": "3D Models",
        "plans_2d": "2D Plans",
        "donnees_techniques": "Technical Data",
        "specifications": "Specifications",
        "calculs": "Calculations",
        "simulations": "Simulations",
        
        // User interface
        "tableau_bord": "Dashboard",
        "menu_principal": "Main Menu",
        "recherche": "Search",
        "filtres": "Filters",
        "tri": "Sort",
        "affichage": "Display",
        "preferences": "Preferences",
        "aide": "Help",
        "support": "Support",
        
        // System messages
        "connexion_reussie": "Connection successful",
        "deconnexion": "Logout",
        "session_expiree": "Session expired",
        "acces_refuse": "Access denied",
        "fichier_introuvable": "File not found",
        "operation_reussie": "Operation successful",
        "operation_echouee": "Operation failed",
        
        // Time and dates
        "aujourd_hui": "Today",
        "hier": "Yesterday",
        "cette_semaine": "This week",
        "ce_mois": "This month",
        "cette_annee": "This year",
        "derniere_mise_a_jour": "Last update",
        "date_creation": "Creation date",
        "date_modification": "Modification date",
        
        // Formats and units
        "pourcentage": "Percentage",
        "nombre": "Number",
        "texte": "Text",
        "date": "Date",
        "heure": "Time",
        "taille": "Size",
        "poids": "Weight",
        "volume": "Volume",
        
        // Notifications
        "nouveau_message": "New message",
        "mise_a_jour_disponible": "Update available",
        "synchronisation_terminee": "Synchronization complete",
        "sauvegarde_automatique": "Auto-save",
        "connexion_perdue": "Connection lost",
        "reconnexion": "Reconnecting...",
        
        // Errors and warnings
        "erreur_connexion": "Connection error",
        "erreur_chargement": "Loading error",
        "erreur_sauvegarde": "Save error",
        "donnees_incompletes": "Incomplete data",
        "format_non_supporte": "Unsupported format",
        "taille_fichier_excessive": "File size too large",
        
        // Confirmation and validation
        "confirmer_action": "Confirm action",
        "action_irreversible": "This action is irreversible",
        "supprimer_definitivement": "Delete permanently?",
        "modifications_non_sauvegardees": "Unsaved changes",
        "voulez_vous_continuer": "Do you want to continue?",
        "operation_annulee": "Operation cancelled",
        
        // User information
        "profil_utilisateur": "User profile",
        "parametres_compte": "Account settings",
        "securite": "Security",
        "notifications": "Notifications",
        "langue": "Language",
        "theme": "Theme",
        "accessibilite": "Accessibility",
        
        // Advanced features
        "mode_avance": "Advanced mode",
        "mode_simple": "Simple mode",
        "personnalisation": "Customization",
        "automatisation": "Automation",
        "intelligence_artificielle": "Artificial Intelligence",
        "machine_learning": "Machine Learning",
        "analyse_predictive": "Predictive Analysis",
        
        // Nouvelles clés ajoutées
        "scores_bimex": "BIMEX Scores",
        "system_operational": "SYSTEM OPERATIONAL",
        "ai_connected": "AI CONNECTED",
        "projects": "Projects",
        "new_generation": "New Generation",
        "add_bim_model": "Add BIM Model (IFC/RVT)",
        "search_project": "Search for a project...",
        "loading_projects": "Loading projects..."
    },
    
    de: {
        // Haupttitel
        "report_title": "BIMEX - Erweiterter BIM-Analysebericht",
        "home_title": "BIMEX - Missionskontrollzentrum",
        "accueil_title": "BIMEX - Missionskontrollzentrum",
        
        // Überschriften und Untertitel
        "mission_control_center": "MISSIONSKONTROLLZENTRUM",
        "intelligence_artificielle": "Künstliche Intelligenz",
        "analyse_avancee": "Erweiterte Analyse",
        "rapport_analyse_bim": "🏗️ ERWEITERTER BIM-ANALYSEBERICHT",
        
        // Navigation und Schaltflächen
        "retour": "Zurück",
        "accueil": "Startseite",
        "telecharger": "Herunterladen",
        "imprimer": "Drucken",
        "partager": "Teilen",
        "fermer": "Schließen",
        "suivant": "Weiter",
        "precedent": "Zurück",
        "valider": "Bestätigen",
        "annuler": "Abbrechen",
        "sauvegarder": "Speichern",
        
        // Aktionen und Zustände
        "demarrer": "Starten",
        "arreter": "Stoppen",
        "pause": "Pause",
        "reprendre": "Fortsetzen",
        "actualiser": "Aktualisieren",
        "reinitialiser": "Zurücksetzen",
        "configurer": "Konfigurieren",
        "analyser": "Analysieren",
        "generer": "Generieren",
        
        // Status und Nachrichten
        "en_cours": "In Bearbeitung",
        "termine": "Abgeschlossen",
        "en_attente": "Ausstehend",
        "erreur": "Fehler",
        "succes": "Erfolg",
        "attention": "Warnung",
        "information": "Information",
        "chargement": "Lädt...",
        "traitement": "Verarbeitung...",
        
        // Berichtsabschnitte
        "resume_executif": "Zusammenfassung",
        "analyse_detaillee": "Detaillierte Analyse",
        "recommandations": "Empfehlungen",
        "conclusion": "Fazit",
        "annexes": "Anhänge",
        "methodologie": "Methodik",
        "resultats": "Ergebnisse",
        "discussion": "Diskussion",
        
        // Metriken und Indikatoren
        "qualite_globale": "Gesamtqualität",
        "score_performance": "Leistungsbewertung",
        "niveau_conformite": "Konformitätsgrad",
        "efficacite": "Effizienz",
        "durabilite": "Nachhaltigkeit",
        "cout_estime": "Geschätzte Kosten",
        "delai_estime": "Geschätzte Zeit",
        "risques": "Risiken",
        "opportunites": "Chancen",
        
        // BIM-Elemente
        "elements_bim": "BIM-Elemente",
        "modeles_3d": "3D-Modelle",
        "plans_2d": "2D-Pläne",
        "donnees_techniques": "Technische Daten",
        "specifications": "Spezifikationen",
        "calculs": "Berechnungen",
        "simulations": "Simulationen",
        
        // Benutzeroberfläche
        "tableau_bord": "Dashboard",
        "menu_principal": "Hauptmenü",
        "recherche": "Suche",
        "filtres": "Filter",
        "tri": "Sortierung",
        "affichage": "Anzeige",
        "preferences": "Einstellungen",
        "aide": "Hilfe",
        "support": "Support",
        
        // Systemnachrichten
        "connexion_reussie": "Verbindung erfolgreich",
        "deconnexion": "Abmelden",
        "session_expiree": "Sitzung abgelaufen",
        "acces_refuse": "Zugriff verweigert",
        "fichier_introuvable": "Datei nicht gefunden",
        "operation_reussie": "Vorgang erfolgreich",
        "operation_echouee": "Vorgang fehlgeschlagen",
        
        // Zeit und Datum
        "aujourd_hui": "Heute",
        "hier": "Gestern",
        "cette_semaine": "Diese Woche",
        "ce_mois": "Dieser Monat",
        "cette_annee": "Dieses Jahr",
        "derniere_mise_a_jour": "Letzte Aktualisierung",
        "date_creation": "Erstellungsdatum",
        "date_modification": "Änderungsdatum",
        
        // Formate und Einheiten
        "pourcentage": "Prozentsatz",
        "nombre": "Anzahl",
        "texte": "Text",
        "date": "Datum",
        "heure": "Zeit",
        "taille": "Größe",
        "poids": "Gewicht",
        "volume": "Volumen",
        
        // Benachrichtigungen
        "nouveau_message": "Neue Nachricht",
        "mise_a_jour_disponible": "Update verfügbar",
        "synchronisation_terminee": "Synchronisation abgeschlossen",
        "sauvegarde_automatique": "Automatisches Speichern",
        "connexion_perdue": "Verbindung verloren",
        "reconnexion": "Wiederverbindung...",
        
        // Fehler und Warnungen
        "erreur_connexion": "Verbindungsfehler",
        "erreur_chargement": "Ladefehler",
        "erreur_sauvegarde": "Speicherfehler",
        "donnees_incompletes": "Unvollständige Daten",
        "format_non_supporte": "Nicht unterstütztes Format",
        "taille_fichier_excessive": "Dateigröße zu groß",
        
        // Bestätigung und Validierung
        "confirmer_action": "Aktion bestätigen",
        "action_irreversible": "Diese Aktion ist unumkehrbar",
        "supprimer_definitivement": "Endgültig löschen?",
        "modifications_non_sauvegardees": "Ungespeicherte Änderungen",
        "voulez_vous_continuer": "Möchten Sie fortfahren?",
        "operation_annulee": "Vorgang abgebrochen",
        
        // Benutzerinformationen
        "profil_utilisateur": "Benutzerprofil",
        "parametres_compte": "Kontoeinstellungen",
        "securite": "Sicherheit",
        "notifications": "Benachrichtigungen",
        "langue": "Sprache",
        "theme": "Design",
        "accessibilite": "Barrierefreiheit",
        
        // Erweiterte Funktionen
        "mode_avance": "Erweiterter Modus",
        "mode_simple": "Einfacher Modus",
        "personnalisation": "Anpassung",
        "automatisation": "Automatisierung",
        "intelligence_artificielle": "Künstliche Intelligenz",
        "machine_learning": "Maschinelles Lernen",
        "analyse_predictive": "Prädiktive Analyse",
        
        // Nouvelles clés ajoutées
        "scores_bimex": "BIMEX-Bewertungen",
        "system_operational": "SYSTEM BETRIEBSBEREIT",
        "ai_connected": "KI VERBUNDEN",
        "projects": "Projekte",
        "new_generation": "Neue Generation",
        "add_bim_model": "BIM-Modell hinzufügen (IFC/RVT)",
        "search_project": "Nach einem Projekt suchen...",
        "loading_projects": "Projekte werden geladen..."
    }
};

// Fonction pour changer la langue
function changeLanguage(lang) {
    if (!translations[lang]) return;
    
    // Mettre à jour les éléments avec l'attribut data-translate
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // Mettre à jour les textes dynamiques
    updateDynamicTexts(lang);
    
    // Mettre à jour les attributs title des boutons de langue
    updateLanguageButtonTitles(lang);
    
    // Mettre à jour l'attribut lang du document
    document.documentElement.lang = lang;
    
    // Stocker la langue préférée
    localStorage.setItem('preferredLanguage', lang);
}

// Fonction pour mettre à jour les textes dynamiques
function updateDynamicTexts(lang) {
    // Mettre à jour les textes des en-têtes
    const headers = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    headers.forEach(header => {
        const text = header.textContent.trim();
        
        // Titres principaux
        if (text.includes('MISSION CONTROL CENTER') || text.includes('CENTRE DE CONTRÔLE DE MISSION') || text.includes('MISSIONSKONTROLLZENTRUM')) {
            header.textContent = translations[lang]['mission_control_center'];
        } else if (text.includes('RAPPORT D\'ANALYSE BIM AVANCÉE') || text.includes('ADVANCED BIM ANALYSIS REPORT') || text.includes('ERWEITERTER BIM-ANALYSEBERICHT')) {
            header.textContent = translations[lang]['rapport_analyse_bim'];
        }
        
        // Sous-titres
        if (text.includes('Intelligence Artificielle') || text.includes('Artificial Intelligence') || text.includes('Künstliche Intelligenz')) {
            header.textContent = translations[lang]['intelligence_artificielle'];
        } else if (text.includes('Analyse Avancée') || text.includes('Advanced Analysis') || text.includes('Erweiterte Analyse')) {
            header.textContent = translations[lang]['analyse_avancee'];
        }
    });
    
    // Mettre à jour les textes des boutons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        const buttonText = button.textContent.trim();
        
        if (buttonText.includes('Retour') || buttonText.includes('Back') || buttonText.includes('Zurück')) {
            button.textContent = translations[lang]['retour'];
        } else if (buttonText.includes('Accueil') || buttonText.includes('Home') || buttonText.includes('Startseite')) {
            button.textContent = translations[lang]['accueil'];
        } else if (buttonText.includes('Télécharger') || buttonText.includes('Download') || buttonText.includes('Herunterladen')) {
            button.textContent = translations[lang]['telecharger'];
        } else if (buttonText.includes('Imprimer') || buttonText.includes('Print') || buttonText.includes('Drucken')) {
            button.textContent = translations[lang]['imprimer'];
        } else if (buttonText.includes('Partager') || buttonText.includes('Share') || buttonText.includes('Teilen')) {
            button.textContent = translations[lang]['partager'];
        } else if (buttonText.includes('Fermer') || buttonText.includes('Close') || buttonText.includes('Schließen')) {
            button.textContent = translations[lang]['fermer'];
        } else if (buttonText.includes('Suivant') || buttonText.includes('Next') || buttonText.includes('Weiter')) {
            button.textContent = translations[lang]['suivant'];
        } else if (buttonText.includes('Précédent') || buttonText.includes('Previous') || buttonText.includes('Zurück')) {
            button.textContent = translations[lang]['precedent'];
        } else if (buttonText.includes('Valider') || buttonText.includes('Validate') || buttonText.includes('Bestätigen')) {
            button.textContent = translations[lang]['valider'];
        } else if (buttonText.includes('Annuler') || buttonText.includes('Cancel') || buttonText.includes('Abbrechen')) {
            button.textContent = translations[lang]['annuler'];
        } else if (buttonText.includes('Sauvegarder') || buttonText.includes('Save') || buttonText.includes('Speichern')) {
            button.textContent = translations[lang]['sauvegarder'];
        }
    });
    
    // Mettre à jour les textes des liens
    const links = document.querySelectorAll('a');
    links.forEach(link => {
        const linkText = link.textContent.trim();
        
        if (linkText.includes('Retour') || linkText.includes('Back') || linkText.includes('Zurück')) {
            link.textContent = translations[lang]['retour'];
        } else if (linkText.includes('Accueil') || linkText.includes('Home') || linkText.includes('Startseite')) {
            link.textContent = translations[lang]['accueil'];
        }
    });
    
    // Mettre à jour les textes des statuts
    const statusElements = document.querySelectorAll('.status, .status-text, .message');
    statusElements.forEach(element => {
        const text = element.textContent.trim();
        
        if (text.includes('En cours') || text.includes('In Progress') || text.includes('In Bearbeitung')) {
            element.textContent = translations[lang]['en_cours'];
        } else if (text.includes('Terminé') || text.includes('Completed') || text.includes('Abgeschlossen')) {
            element.textContent = translations[lang]['termine'];
        } else if (text.includes('En attente') || text.includes('Pending') || text.includes('Ausstehend')) {
            element.textContent = translations[lang]['en_attente'];
        } else if (text.includes('Erreur') || text.includes('Error') || text.includes('Fehler')) {
            element.textContent = translations[lang]['erreur'];
        } else if (text.includes('Succès') || text.includes('Success') || text.includes('Erfolg')) {
            element.textContent = translations[lang]['succes'];
        }
    });
}

// Fonction pour mettre à jour les titres des boutons de langue
function updateLanguageButtonTitles(lang) {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        const langCode = btn.getAttribute('data-lang');
        if (langCode === 'fr') {
            btn.setAttribute('title', 'Français');
        } else if (langCode === 'en') {
            btn.setAttribute('title', 'English');
        } else if (langCode === 'de') {
            btn.setAttribute('title', 'Deutsch');
        }
    });
}

// Fonctions utilitaires
function getCurrentLanguage() {
    return localStorage.getItem('preferredLanguage') || 'fr';
}

function hasTranslation(key, lang) {
    return translations[lang] && translations[lang][key];
}

function getTranslation(key, lang) {
    return translations[lang] && translations[lang][key] ? translations[lang][key] : key;
}

// Initialiser la langue au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'fr';
    changeLanguage(savedLanguage);
    
    // Ajouter les écouteurs d'événements pour les boutons de langue
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const lang = this.getAttribute('data-lang');
            changeLanguage(lang);
        });
    });
});
