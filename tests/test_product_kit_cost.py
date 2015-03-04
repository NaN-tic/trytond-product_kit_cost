# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from decimal import Decimal
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT, test_view,\
    test_depends
from trytond.transaction import Transaction


class TestCase(unittest.TestCase):
    'Test module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('product_kit_cost')
        self.uom = POOL.get('product.uom')
        self.uom_category = POOL.get('product.uom.category')
        self.template = POOL.get('product.template')
        self.product = POOL.get('product.product')
        self.category = POOL.get('product.category')
        self.kit_line = POOL.get('product.kit.line')

    def test0005views(self):
        'Test views'
        test_view('product_kit_cost')

    def test0006depends(self):
        'Test depends'
        test_depends()

    def test0060cost_price_kit(self):
        'Test cost price kit calculation'

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            uom, = self.uom.search([], limit=1)
            kit1 = {
                'name': 'Kit 1',
                'type': 'goods',
                'list_price': Decimal('50'),
                'cost_price': Decimal('5'),
                'default_uom': uom.id,
                'products': [('create', [{}])],
                }

            kit1_1 = {
                    'name': 'Kit 1.1',
                    'type': 'goods',
                    'list_price': Decimal('20'),
                    'cost_price': Decimal('5'),
                    'default_uom': uom.id,
                    'products': [('create', [{}])],
                    }

            cop1 = {
                    'name': 'Comp1',
                    'type': 'goods',
                    'list_price': Decimal('10'),
                    'cost_price': Decimal('5'),
                    'default_uom': uom.id,
                    'products': [('create', [{}])],
                    }

            cop2 = {
                    'name': 'Comp2',
                    'type': 'goods',
                    'list_price': Decimal('10'),
                    'cost_price': Decimal('5'),
                    'default_uom': uom.id,
                    'products': [('create', [{}])],
                    }
            cop3 = {
                    'name': 'Comp3',
                    'type': 'goods',
                    'list_price': Decimal('10'),
                    'cost_price': Decimal('5'),
                    'default_uom': uom.id,
                    'products': [('create', [{}])],
                    }

            kt1, kt11, tc1, tc2, tc3 = self.template.create([kit1, kit1_1,
                cop1, cop2, cop3])

            kit1, = kt1.products
            kit11, = kt11.products
            comp1, = tc1.products
            comp2, = tc2.products
            comp3, = tc3.products

            kit1.kit = True
            kit1.save()
            kit11.kit = True
            kit11.save()

            k11l1 = self.kit_line()
            k11l1.product = comp2
            k11l1.quantity = 1
            k11l1.unit = uom
            k11l1.parent = kit11
            k11l1.save()

            k11l2 = self.kit_line()
            k11l2.product = comp3
            k11l2.quantity = 2
            k11l2.unit = uom
            k11l2.parent = kit11
            k11l2.save()

            k1l1 = self.kit_line()
            k1l1.product = comp1
            k1l1.quantity = 1
            k1l1.unit = uom
            k1l1.parent = kit1
            k1l1.save()

            k1l2 = self.kit_line()
            k1l2.product = kit11
            k1l2.quantity = 2
            k1l2.unit = uom
            k1l2.parent = kit1
            k1l2.save()

            # test kit11
            # sale_price = 20
            # cost_price = 5 + 2*5 = 15
            # cost_margin = 20-15 = 5
            # cost_margin_percent =  1-15/20
            self.assertEqual(kit11.kit_cost_price, Decimal('15'))
            # test kit11
            # sale_price = 50
            # cost_price = kit11(5 + 2*5 = 15)*2 + 5  = 35
            # cost_margin = 50-35 = 15
            # cost_margin_percent = 1-35/50
            self.assertEqual(kit1.kit_cost_price, Decimal('35'))


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCase))
    return suite
