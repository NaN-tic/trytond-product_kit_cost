# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Bool
from trytond.config import config

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
        # Remove factor on screen
        if field_name == 'kit_margin_percent':
            value = value / Decimal('100.0')
        products = cls.search([('kit', '=', True)])
        product_ids = []
        for product in products:
            product_value = getattr(product, field_name)
            insert = False
            if operator == '=':
                insert = product_value == value
            elif operator == '!=':
                insert = product_value != value
            elif operator == '<':
                insert = product_value < value
            elif operator == '<=':
                insert = product_value <= value
            elif operator == '>':
                insert = product_value > value
            elif operator == '>=':
                insert = product_value >= value
            if insert:
                product_ids.append(product.id)
        return [('id', 'in', product_ids)]

    @classmethod
    def get_kit_cost_price(cls, products, names):
        prices = {}
        for name in ['kit_cost_price', 'kit_margin', 'kit_margin_percent']:
            prices[name] = {}

        for product in products:
            price = product._get_kit_cost_price()
            prices['kit_cost_price'][product.id] = price
            if product.list_price and price:
                prices['kit_margin'][product.id] = product.list_price - price
                prices['kit_margin_percent'][product.id] = (1 -
                    price / product.list_price)
            else:
                prices['kit_margin'][product.id] = _ZERO
                prices['kit_margin_percent'][product.id] = _ZERO
        return prices
