# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.

from decimal import Decimal
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Bool
from trytond.config import config
from trytond.tools import safe_eval

DIGITS = config.getint('digits', 'unit_price_digits', 4)

__all__ = ['Product']
__metaclass__ = PoolMeta

_ZERO = Decimal('0.0')

STATES = {
    'invisible': Bool(~Eval('kit')),
}

DEPENDS = ['kit']


class Product:
    __name__ = 'product.product'

    kit_cost_price = fields.Function(fields.Numeric('Kit Cost',
        digits=(16, DIGITS), states=STATES,
            depends=DEPENDS), 'get_kit_cost_price',
        searcher='search_kit_cost_price')
    kit_margin = fields.Function(fields.Numeric('Kit Margin',
        digits=(16, DIGITS), states=STATES,
            depends=DEPENDS), 'get_kit_cost_price',
        searcher='search_kit_cost_price')
    kit_margin_percent = fields.Function(fields.Numeric('Kit Margin(%)',
        digits=(16, DIGITS), states=STATES,
            depends=DEPENDS), 'get_kit_cost_price',
        searcher='search_kit_cost_price')

    def _get_kit_cost_price(self):
        if not self.kit:
            return self.cost_price
        Uom = Pool().get('product.uom')
        price = _ZERO
        for line in self.kit_lines:
            price += (Decimal(str(line.quantity)) *
                Uom.compute_price(line.product.default_uom,
                    line.product._get_kit_cost_price(), line.unit))
        return price

    @classmethod
    def search_kit_cost_price(cls, names, clause):
        field_name, operator, value = clause
        products = cls.search([('kit', '=', True)])
        prices = cls.get_kit_cost_price(products, names)
        product_ids = []
        for product_id, val in prices.get(field_name).iteritems():
            exp = ('%(val)s ' + operator + '%(value)s') % locals()
            res_exp = safe_eval(exp)
            if res_exp:
                product_ids.append(product_id)
        return [('id', 'in', product_ids)]

    @classmethod
    def get_kit_cost_price(cls, products, names):
        prices = {}
        for name in ['kit_cost_price', 'kit_margin', 'kit_margin_percent']:
            prices[name] = {}

        for product in products:
            price = product._get_kit_cost_price()
            prices['kit_cost_price'][product.id] = price
            prices['kit_margin'][product.id] = product.list_price - price
            prices['kit_margin_percent'][product.id] = (1 -
                price / product.list_price)

        return prices
