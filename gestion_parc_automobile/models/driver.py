# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class FleetDriver(models.Model):
    _name = 'fleet.driver'
    _description = 'Chauffeur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string="Nom complet", required=True, tracking=True)
    code = fields.Char(string="Matricule", readonly=True, copy=False, default=lambda self: _('Nouveau'))

    # Informations personnelles
    phone = fields.Char(string="Téléphone")
    mobile = fields.Char(string="Mobile")
    email = fields.Char(string="Email")
    address = fields.Text(string="Adresse")

    # Permis
    license_number = fields.Char(string="N° de permis", tracking=True)
    license_type = fields.Selection([
        ('A', 'A - Moto'),
        ('B', 'B - Voiture'),
        ('C', 'C - Poids lourd'),
        ('D', 'D - Transport en commun'),
        ('E', 'E - Remorque'),
    ], string="Catégorie de permis", tracking=True)
    license_expiry = fields.Date(string="Date d'expiration du permis", tracking=True)

    # Organisation
    department_id = fields.Many2one('hr.department', string="Service / Direction")
    employee_id = fields.Many2one('hr.employee', string="Employé lié")
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company)

    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('suspended', 'Suspendu'),
    ], string="État", default='draft', tracking=True)

    active = fields.Boolean(default=True)
    notes = fields.Text(string="Notes")
    image_128 = fields.Image("Photo", max_width=128, max_height=128)

    # Relations
    assignment_ids = fields.One2many('fleet.assignment', 'driver_id', string="Affectations")
    vehicle_ids = fields.One2many('fleet.vehicle', 'driver_id', string="Véhicules actuels")

    assignment_count = fields.Integer(compute='_compute_assignment_count')

    _sql_constraints = [
        ('license_number_uniq', 'unique(license_number)', 'Ce numéro de permis existe déjà !'),
    ]

    @api.depends('assignment_ids')
    def _compute_assignment_count(self):
        for record in self:
            record.assignment_count = len(record.assignment_ids)

    @api.constrains('license_expiry')
    def _check_license_expiry(self):
        for record in self:
            if record.license_expiry and record.license_expiry < date.today():
                # On laisse passer mais on peut mettre un warning
                pass

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _('Nouveau')) == _('Nouveau'):
                vals['code'] = self.env['ir.sequence'].next_by_code('fleet.driver') or _('Nouveau')
        return super().create(vals_list)

    def action_set_active(self):
        self.write({'state': 'active'})

    def action_set_inactive(self):
        self.write({'state': 'inactive'})