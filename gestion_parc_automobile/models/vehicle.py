# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date


class FleetVehicle(models.Model):
    _name = 'fleet.vehicle'
    _description = 'Véhicule du Parc Automobile'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # ==================== Identification ====================
    name = fields.Char(
        string="Nom / Désignation",
        required=True,
        tracking=True,
        help="Ex: Toyota Corolla - Direction Générale"
    )
    license_plate = fields.Char(
        string="Immatriculation",
        required=True,
        tracking=True,
        copy=False,
        index=True
    )
    code = fields.Char(
        string="Code interne",
        readonly=True,
        copy=False,
        default=lambda self: _('Nouveau')
    )

    # ==================== Caractéristiques ====================
    brand = fields.Char(string="Marque", tracking=True)
    model = fields.Char(string="Modèle", tracking=True)
    category = fields.Char(string="Catégorie", tracking=True)

    vehicle_type = fields.Selection([
        ('car', 'Voiture'),
        ('van', 'Camionnette'),
        ('truck', 'Camion'),
        ('bus', 'Bus'),
        ('motorcycle', 'Moto'),
        ('other', 'Autre'),
    ], string="Type de véhicule", default='car', tracking=True)

    year = fields.Integer(string="Année de mise en circulation", tracking=True)
    color = fields.Char(string="Couleur")
    chassis_number = fields.Char(string="N° de châssis (VIN)")
    engine_number = fields.Char(string="N° de moteur")

    fuel_type = fields.Selection([
        ('diesel', 'Diesel'),
        ('gasoline', 'Essence'),
        ('hybrid', 'Hybride'),
        ('electric', 'Électrique'),
        ('lpg', 'GPL'),
    ], string="Type de carburant", default='diesel', tracking=True)

    seats = fields.Integer(string="Nombre de places", default=5)
    doors = fields.Integer(string="Nombre de portes", default=4)

    # ==================== État et Kilométrage ====================
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('available', 'Disponible'),
        ('assigned', 'Affecté'),
        ('maintenance', 'En entretien'),
        ('out_of_service', 'Hors service'),
        ('sold', 'Vendu'),
    ], string="État", default='draft', tracking=True)

    odometer = fields.Float(
        string="Kilométrage actuel (km)",
        tracking=True,
        help="Dernier kilométrage enregistré"
    )
    odometer_unit = fields.Selection([
        ('kilometers', 'Kilomètres'),
        ('miles', 'Miles'),
    ], default='kilometers', string="Unité")

    acquisition_date = fields.Date(string="Date d'acquisition", tracking=True)
    acquisition_price = fields.Float(string="Prix d'acquisition")

    # ==================== Organisation ====================
    department_id = fields.Many2one('hr.department', string="Direction / Service")
    company_id = fields.Many2one(
        'res.company',
        string="Société",
        default=lambda self: self.env.company,
        required=True
    )
    driver_id = fields.Many2one(
        'fleet.driver',
        string="Chauffeur actuel",
        tracking=True
    )
    location = fields.Char(string="Localisation actuelle")

    # ==================== Relations ====================
    assignment_ids = fields.One2many('fleet.assignment', 'vehicle_id', string="Historique des affectations")
    maintenance_ids = fields.One2many('fleet.maintenance', 'vehicle_id', string="Entretiens")
    fuel_log_ids = fields.One2many('fleet.fuel.log', 'vehicle_id', string="Consommations carburant")
    insurance_ids = fields.One2many('fleet.insurance', 'vehicle_id', string="Assurances")
    technical_control_ids = fields.One2many('fleet.technical.control', 'vehicle_id', string="Contrôles techniques")
    claim_ids = fields.One2many('fleet.claim', 'vehicle_id', string="Sinistres")

    # ==================== Champs calculés ====================
    assignment_count = fields.Integer(compute='_compute_counts', string="Nb Affectations")
    maintenance_count = fields.Integer(compute='_compute_counts', string="Nb Entretiens")
    fuel_count = fields.Integer(compute='_compute_counts', string="Nb Plein")
    claim_count = fields.Integer(compute='_compute_counts', string="Nb Sinistres")

    total_fuel_cost = fields.Float(compute='_compute_costs', string="Coût carburant total", store=True)
    total_maintenance_cost = fields.Float(compute='_compute_costs', string="Coût entretiens total", store=True)
    total_insurance_cost = fields.Float(compute='_compute_costs', string="Coût assurances total", store=True)
    total_claim_cost = fields.Float(compute='_compute_costs', string="Coût sinistres total", store=True)
    total_operating_cost = fields.Float(compute='_compute_costs', string="Coût total d'exploitation", store=True)

    next_insurance_date = fields.Date(compute='_compute_next_dates', string="Prochaine échéance assurance")
    next_technical_date = fields.Date(compute='_compute_next_dates', string="Prochain contrôle technique")
    next_maintenance_date = fields.Date(compute='_compute_next_dates', string="Prochain entretien")

    active = fields.Boolean(default=True)
    notes = fields.Text(string="Notes / Observations")
    image_128 = fields.Image("Image", max_width=128, max_height=128)

    # ==================== Contraintes SQL ====================
    _sql_constraints = [
        ('license_plate_uniq', 'unique(license_plate)', 'Cette immatriculation existe déjà !'),
        ('code_uniq', 'unique(code)', 'Ce code interne existe déjà !'),
    ]

    # ==================== Contraintes métier ====================
    @api.constrains('odometer')
    def _check_odometer(self):
        for record in self:
            if record.odometer < 0:
                raise ValidationError(_("Le kilométrage ne peut pas être négatif."))

    @api.constrains('year')
    def _check_year(self):
        current_year = date.today().year
        for record in self:
            if record.year and (record.year < 1980 or record.year > current_year + 1):
                raise ValidationError(_("L'année de mise en circulation semble incorrecte."))

    # ==================== Méthodes de calcul ====================
    @api.depends('assignment_ids', 'maintenance_ids', 'fuel_log_ids', 'claim_ids')
    def _compute_counts(self):
        for record in self:
            record.assignment_count = len(record.assignment_ids)
            record.maintenance_count = len(record.maintenance_ids)
            record.fuel_count = len(record.fuel_log_ids)
            record.claim_count = len(record.claim_ids)

    @api.depends('fuel_log_ids.total_amount', 'maintenance_ids.cost',
                 'insurance_ids.amount', 'claim_ids.cost')
    def _compute_costs(self):
        for record in self:
            record.total_fuel_cost = sum(record.fuel_log_ids.mapped('total_amount'))
            record.total_maintenance_cost = sum(record.maintenance_ids.mapped('cost'))
            record.total_insurance_cost = sum(record.insurance_ids.mapped('amount'))
            record.total_claim_cost = sum(record.claim_ids.mapped('cost'))
            record.total_operating_cost = (
                record.total_fuel_cost +
                record.total_maintenance_cost +
                record.total_insurance_cost +
                record.total_claim_cost
            )

    def _compute_next_dates(self):
        for record in self:
            insurances = record.insurance_ids.filtered(lambda i: i.end_date).sorted('end_date')
            record.next_insurance_date = insurances[0].end_date if insurances else False

            controls = record.technical_control_ids.filtered(lambda c: c.next_date).sorted('next_date')
            record.next_technical_date = controls[0].next_date if controls else False

            maintenances = record.maintenance_ids.filtered(lambda m: m.next_date).sorted('next_date')
            record.next_maintenance_date = maintenances[0].next_date if maintenances else False

    # ==================== CRUD ====================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _('Nouveau')) == _('Nouveau'):
                vals['code'] = self.env['ir.sequence'].next_by_code('fleet.vehicle') or _('Nouveau')
        return super().create(vals_list)

    def write(self, vals):
        if 'odometer' in vals:
            for record in self:
                if vals['odometer'] < record.odometer:
                    raise UserError(_("Le kilométrage ne peut pas diminuer (actuel : %s km).") % record.odometer)
        return super().write(vals)

    # ==================== Actions boutons ====================
    def action_set_available(self):
        self.write({'state': 'available'})

    def action_set_maintenance(self):
        self.write({'state': 'maintenance'})

    def action_set_out_of_service(self):
        self.write({'state': 'out_of_service'})

    def action_view_assignments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Affectations'),
            'res_model': 'fleet.assignment',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }

    def action_view_maintenances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Entretiens'),
            'res_model': 'fleet.maintenance',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }

    def action_view_fuel_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Consommations'),
            'res_model': 'fleet.fuel.log',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }