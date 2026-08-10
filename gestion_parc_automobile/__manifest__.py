# -*- coding: utf-8 -*-
{
    'name': "Gestion du Parc Automobile",
    'version': '18.0.1.0.0',
    'category': 'Fleet',
    'summary': "Gestion complète du parc automobile : véhicules, chauffeurs, affectations, entretiens, carburant, assurances, sinistres et coûts",
    'description': """
Module de Gestion du Parc Automobile
====================================

Ce module permet la gestion centralisée et complète d'un parc automobile :

* Gestion des véhicules avec historique complet
* Gestion des chauffeurs et informations administratives
* Affectation des véhicules aux chauffeurs ou services
* Entretiens préventifs et curatifs
* Consommations de carburant
* Assurances et suivi des échéances
* Contrôles techniques
* Gestion des sinistres et incidents
* Suivi des coûts d'exploitation par véhicule
* Tableaux de bord et indicateurs de performance (KPI)
* Notifications automatiques des échéances
* Rapports PDF et exports

Développé dans le cadre d'un projet intégrateur.
    """,
    'author': "Groupe Examen ISI",
    'website': "https://www.votre-site.com",
    'license': 'LGPL-3',

    'depends': [
        'base',
        'mail',
        'hr',
    ],

    'data': [
        # Sécurité
        'security/ir.model.access.csv',
        'data/sequences.xml',

        # Vues
        'views/vehicle_views.xml',
        'views/driver_views.xml',
        'views/assignment_views.xml',
        'views/maintenance_views.xml',
        'views/fuel_views.xml',
        'views/insurance_views.xml',
        'views/technical_control_views.xml',
        'views/claim_views.xml',
        'views/partner_garage_views.xml',
        'views/menus.xml',
        'report/vehicle_report_templates.xml',
        'report/vehicle_report.xml',

        # Données de démonstration
        'data/demo_data.xml',
    ],

    'demo': [],

    'assets': {
        'web.assets_backend': [
            # 'gestion_parc_automobile/static/src/css/parc.css',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 10,
}