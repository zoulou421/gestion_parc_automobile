# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetFuelLog(models.Model):
    _name = 'fleet.fuel.log'
    _description = 'Consommation de carburant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string="Référence", readonly=True, copy=False, default=lambda self: _('Nouveau'))

    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule", required=True, tracking=True, ondelete='restrict')
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today, tracking=True)

    liter = fields.Float(string="Litres", required=True, tracking=True)
    price_per_liter = fields.Float(string="Prix au litre")
    total_amount = fields.Float(string="Montant total", compute='_compute_total_amount', store=True)

    odometer = fields.Float(string="Kilométrage au moment du plein")
    fuel_type = fields.Selection(related='vehicle_id.fuel_type', store=True, string="Type de carburant")

    station = fields.Char(string="Station-service")
    inv_ref = fields.Char(string="N° de facture / ticket")

    notes = fields.Text(string="Notes")
    company_id = fields.Many2one('res.company', related='vehicle_id.company_id', store=True)

    @api.depends('liter', 'price_per_liter')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.liter * record.price_per_liter

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fleet.fuel.log') or _('Nouveau')
        return super().create(vals_list)