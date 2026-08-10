# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FleetAssignment(models.Model):
    _name = 'fleet.assignment'
    _description = 'Affectation de véhicule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(string="Référence", readonly=True, copy=False, default=lambda self: _('Nouveau'))

    vehicle_id = fields.Many2one('fleet.vehicle', string="Véhicule", required=True, tracking=True, ondelete='restrict')
    driver_id = fields.Many2one('fleet.driver', string="Chauffeur", tracking=True, ondelete='restrict')
    department_id = fields.Many2one('hr.department', string="Service / Direction", tracking=True)

    date_start = fields.Date(string="Date de début", required=True, tracking=True, default=fields.Date.context_today)
    date_end = fields.Date(string="Date de fin", tracking=True)

    assignment_type = fields.Selection([
        ('driver', 'Affecté à un chauffeur'),
        ('department', 'Affecté à un service'),
        ('pool', 'Véhicule de pool'),
    ], string="Type d'affectation", default='driver', required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('running', 'En cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string="État", default='draft', tracking=True)

    odometer_start = fields.Float(string="Kilométrage au départ")
    odometer_end = fields.Float(string="Kilométrage au retour")

    notes = fields.Text(string="Notes / Motif")
    company_id = fields.Many2one('res.company', related='vehicle_id.company_id', store=True)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_end and record.date_end < record.date_start:
                raise ValidationError(_("La date de fin doit être postérieure à la date de début."))

    @api.constrains('vehicle_id', 'date_start', 'date_end', 'state')
    def _check_vehicle_availability(self):
        for record in self:
            if record.state not in ('running', 'draft'):
                continue
            domain = [
                ('vehicle_id', '=', record.vehicle_id.id),
                ('id', '!=', record.id),
                ('state', '=', 'running'),
            ]
            overlapping = self.search(domain)
            if overlapping:
                raise ValidationError(_(
                    "Le véhicule %s est déjà affecté (affectation : %s)."
                ) % (record.vehicle_id.name, overlapping[0].name))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('fleet.assignment') or _('Nouveau')
        return super().create(vals_list)

    def action_start(self):
        for record in self:
            record.write({'state': 'running'})
            # Mettre à jour le véhicule
            record.vehicle_id.write({
                'state': 'assigned',
                'driver_id': record.driver_id.id if record.driver_id else False,
            })

    def action_done(self):
        for record in self:
            record.write({'state': 'done', 'date_end': fields.Date.context_today(record)})
            record.vehicle_id.write({
                'state': 'available',
                'driver_id': False,
            })

    def action_cancel(self):
        self.write({'state': 'cancelled'})