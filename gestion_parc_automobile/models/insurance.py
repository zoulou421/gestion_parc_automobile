# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetInsurance(models.Model):
    _name = 'fleet.insurance'
    _description = 'Assurance véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'end_date desc'

    name = fields.Char(string="N° de police", required=True, tracking=True)

    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule", required=True, tracking=True, ondelete='restrict')
    insurer_id = fields.Many2one('res.partner', string="Compagnie d'assurance", required=True)

    start_date = fields.Date(string="Date de début", required=True, tracking=True)
    end_date = fields.Date(string="Date de fin", required=True, tracking=True)

    insurance_type = fields.Selection([
        ('third_party', 'Responsabilité civile'),
        ('third_party_fire_theft', 'Tiers + Vol + Incendie'),
        ('comprehensive', 'Tous risques'),
        ('other', 'Autre'),
    ], string="Type d'assurance", default='comprehensive', tracking=True)

    amount = fields.Float(string="Prime annuelle", tracking=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('running', 'En cours'),
        ('expired', 'Expirée'),
        ('cancelled', 'Résiliée'),
    ], string="État", default='draft', tracking=True, compute='_compute_state', store=True)

    notes = fields.Text(string="Notes")
    company_id = fields.Many2one('res.company', related='vehicle_id.company_id', store=True)

    @api.depends('end_date')
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.end_date and record.end_date < today:
                record.state = 'expired'
            elif record.state == 'draft':
                record.state = 'draft'
            else:
                record.state = 'running'