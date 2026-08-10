# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_garage = fields.Boolean(
        string="Garage / Fournisseur automobile",
        help="Cochez cette case si ce contact est un garage, un fournisseur de pièces "
             "ou un prestataire d'entretien pour le parc automobile."
    )
    garage_specialty = fields.Selection([
        ('general', 'Entretien général'),
        ('mechanic', 'Mécanique'),
        ('bodywork', 'Carrosserie'),
        ('tires', 'Pneumatiques'),
        ('electrical', 'Électricité auto'),
        ('other', 'Autre'),
    ], string="Spécialité")
    maintenance_count = fields.Integer(compute='_compute_maintenance_count', string="Nb Entretiens")

    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = self.env['fleet.maintenance'].search_count(
                [('garage_id', '=', record.id)]
            )

    def action_view_maintenances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Entretiens',
            'res_model': 'fleet.maintenance',
            'view_mode': 'list,form',
            'domain': [('garage_id', '=', self.id)],
            'context': {'default_garage_id': self.id},
        }