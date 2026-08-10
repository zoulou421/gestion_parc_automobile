# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetClaim(models.Model):
    _name = 'fleet.claim'
    _description = 'Sinistre / Incident'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string="Référence", readonly=True, copy=False, default=lambda self: _('Nouveau'))

    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule", required=True, tracking=True, ondelete='restrict')
    driver_id = fields.Many2one('fleet.driver', string="Chauffeur impliqué", tracking=True)

    date = fields.Date(string="Date du sinistre", required=True, default=fields.Date.context_today, tracking=True)
    claim_type = fields.Selection([
        ('accident', 'Accident'),
        ('theft', 'Vol'),
        ('vandalism', 'Vandalisme'),
        ('fire', 'Incendie'),
        ('glass', 'Bris de glace'),
        ('other', 'Autre'),
    ], string="Type de sinistre", required=True, tracking=True)

    description = fields.Text(string="Description", required=True)
    location = fields.Char(string="Lieu")

    cost = fields.Float(string="Coût estimé / réel", tracking=True)
    insurance_covered = fields.Boolean(string="Pris en charge par l'assurance")
    insurance_refund = fields.Float(string="Montant remboursé")

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('declared', 'Déclaré'),
        ('in_progress', 'En cours de traitement'),
        ('closed', 'Clôturé'),
        ('cancelled', 'Annulé'),
    ], string="État", default='draft', tracking=True)

    company_id = fields.Many2one('res.company', related='vehicle_id.company_id', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fleet.claim') or _('Nouveau')
        return super().create(vals_list)

    def action_declare(self):
        self.write({'state': 'declared'})

    def action_close(self):
        self.write({'state': 'closed'})