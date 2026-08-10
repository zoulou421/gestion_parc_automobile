# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetTechnicalControl(models.Model):
    _name = 'fleet.technical.control'
    _description = 'Contrôle technique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string="Référence", readonly=True, copy=False, default=lambda self: _('Nouveau'))

    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule", required=True, tracking=True, ondelete='restrict')
    date = fields.Date(string="Date du contrôle", required=True, default=fields.Date.context_today, tracking=True)
    next_date = fields.Date(string="Prochaine échéance", tracking=True)

    result = fields.Selection([
        ('passed', 'Favorable'),
        ('passed_with_observations', 'Favorable avec observations'),
        ('failed', 'Défavorable'),
    ], string="Résultat", required=True, tracking=True)

    center = fields.Char(string="Centre de contrôle")
    cost = fields.Float(string="Coût")
    notes = fields.Text(string="Observations")

    company_id = fields.Many2one('res.company', related='vehicle_id.company_id', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fleet.technical.control') or _('Nouveau')
        return super().create(vals_list)