# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetMaintenance(models.Model):
    _name = 'fleet.maintenance'
    _description = 'Entretien de véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string="Référence", readonly=True, copy=False, default=lambda self: _('Nouveau'))

    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule", required=True, tracking=True, ondelete='restrict')
    maintenance_type = fields.Selection([
        ('preventive', 'Préventif'),
        ('corrective', 'Curatif'),
        ('revision', 'Révision'),
        ('repair', 'Réparation'),
        ('tire', 'Pneus'),
        ('other', 'Autre'),
    ], string="Type d'entretien", required=True, default='preventive', tracking=True)

    date = fields.Date(string="Date", required=True, default=fields.Date.context_today, tracking=True)
    next_date = fields.Date(string="Prochaine échéance")
    odometer = fields.Float(string="Kilométrage")

    garage_id = fields.Many2one('res.partner', string="Garage / Fournisseur", domain="[('is_garage', '=', True)]")
    cost = fields.Float(string="Coût (HT)", tracking=True)
    description = fields.Text(string="Description des travaux")

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planned', 'Planifié'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string="État", default='draft', tracking=True)

    company_id = fields.Many2one('res.company', related='vehicle_id.company_id', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fleet.maintenance') or _('Nouveau')
        return super().create(vals_list)

    def action_plan(self):
        self.write({'state': 'planned'})

    def action_start(self):
        self.write({'state': 'in_progress'})
        self.vehicle_id.write({'state': 'maintenance'})

    def action_done(self):
        self.write({'state': 'done'})
        self.vehicle_id.write({'state': 'available'})