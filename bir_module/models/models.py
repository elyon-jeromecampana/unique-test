# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import psycopg2


class bir_module(models.Model):
    _name = 'bir_module.bir_module'
    _description = 'bir_module.bir_module'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

class setup_2550(models.Model):
    _name = 'bir_module.setup_2550'
    _description = 'Form 2550 Setup for expense'

    name = fields.Many2one('account.account', domain="[('internal_group', '=', 'expense')]")    

class bir_reports(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    test_field = fields.Char()

    @api.model
    def get_bir_quarter(self, value):
        quarter = 0
        month = value.month

        if month <= 4: quarter = 1
        elif month <= 8 and month > 4: quarter = 2
        elif month <= 12 and month > 8: quarter = 3
        else: quarter = 1

        return quarter

    def get_monthly_sales_vat(self, value, const, q_index):
        doc_month = value.month
        query = "SELECT D.name,D.amount,B.price_subtotal,F.name FROM account_move A "
        query += "LEFT JOIN account_move_line B ON B.move_id = A.id AND B.exclude_from_invoice_tab = 'false' "
        query += "INNER JOIN account_move_line_account_tax_rel C ON C.account_move_line_id = B.id "
        query += "LEFT JOIN account_tax D ON D.id = C.account_tax_id "
        query += "LEFT JOIN res_partner E ON E.id = A.partner_id "
        query += "LEFT JOIN res_partner_industry F ON F.id = E.industry_id "
        if const == 'quar':
            if q_index == 1:
                query += "WHERE EXTRACT(MONTH FROM A.date) = '1' AND EXTRACT(MONTH FROM A.date) = '2' AND EXTRACT(MONTH FROM A.date) = '3' AND EXTRACT(MONTH FROM A.date) = '4' AND A.move_type = 'out_invoice' AND a.state = 'posted'"
            elif q_index == 2:
                query += "WHERE EXTRACT(MONTH FROM A.date) = '5' AND EXTRACT(MONTH FROM A.date) = '6' AND EXTRACT(MONTH FROM A.date) = '7' AND EXTRACT(MONTH FROM A.date) = '8' AND A.move_type = 'out_invoice' AND a.state = 'posted'"
            else:
                query += "WHERE EXTRACT(MONTH FROM A.date) = '9' AND EXTRACT(MONTH FROM A.date) = '10' AND EXTRACT(MONTH FROM A.date) = '11' AND EXTRACT(MONTH FROM A.date) = '12' AND A.move_type = 'out_invoice' AND a.state = 'posted'"
        else:
            query += "WHERE EXTRACT(MONTH FROM A.date) = '" + str(doc_month) + "' AND A.move_type = 'out_invoice' AND a.state = 'posted'"

        self._cr.execute(query)
        val = self._cr.fetchall()

        zero_rated = 0
        vat_private,private_sub,vat_govt,govt_sub = 0,0,0,0
        sub_total,vat_total = 0,0
        # private_sub = 0
        # vat_govt = 0
        # govt_sub = 0
        ret = []
        for sub in val:
            if sub[1] == 0:
                zero_rated += sub[2]
            else:
                if sub[3] != 'Government':
                    vat_private += ((sub[1]/100)*sub[2])
                    private_sub += sub[2]
                else:
                    vat_govt += ((sub[1]/100)*sub[2])
                    govt_sub += sub[2]
        sub_total = private_sub + govt_sub
        vat_total = vat_private + vat_govt
        return [round(vat_private,2),round(private_sub,2),round(vat_govt,2),round(govt_sub,2),round(zero_rated,2),round(sub_total,2),round(vat_total,2)]

    def get_monthly_purchase_vat(self, value):
        expense = self.get_purchase_account()
        doc_month = value.month
        query = "SELECT D.name,D.amount,B.price_subtotal,B.debit,F.name,A.move_type,D.tax_scope FROM account_move A "
        query += "LEFT JOIN account_move_line B ON B.move_id = A.id AND B.exclude_from_invoice_tab = 'false' "
        query += "INNER JOIN account_move_line_account_tax_rel C ON C.account_move_line_id = B.id "
        query += "LEFT JOIN account_tax D ON D.id = C.account_tax_id "
        query += "LEFT JOIN res_partner E ON E.id = A.partner_id "
        query += "LEFT JOIN res_partner_industry F ON F.id = E.industry_id "
        query += "WHERE EXTRACT(MONTH FROM A.date) = '" + str(doc_month) + "' AND (A.move_type = 'in_invoice' OR "

        ctr = 1
        for exp in expense:
            query += "(B.account_id = '" + str(exp[0]) + "' AND A.move_type = 'entry')"
            if ctr != len(expense):
                query += " OR "
            ctr += 1
        query += ") AND a.state = 'posted'"

        self._cr.execute(query)
        val = self._cr.fetchall()

        # vat_goods,goods_sub = 0,0
        # vat_service,service_sub = 0,0
        # for sub in val:
        #     if sub[5] == 'consu' or sub[5] == '':
        #         goods_sub += sub[2]
        #         vat_goods += ((sub[1]/100)*sub[2])
        #     elif sub[5] == 'service':
        #         service_sub += sub[2]
        #         vat_service += ((sub[1]/100)*sub[2])

        # return [round(goods_sub,0),round(vat_goods,0),round(service_sub,0),round(vat_service,0)], val
        return val

    def get_purchase_account(self):
        query = "SELECT name FROM bir_module_setup_2550"
        self._cr.execute(query)
        return self._cr.fetchall()

    def month_or_quarter(self, value):
        val = []
        if value.month == 4:
            val = self.get_monthly_sales_vat(value, 'quar', 1)
        elif value.month == 8:
            val = self.get_monthly_sales_vat(value, 'quar', 2)
        elif value.month == 12:
            val = self.get_monthly_sales_vat(value, 'quar', 3)
        else:
            val = self.get_monthly_sales_vat(value, 'mos', 0)

        return val
