#!/usr/bin/env python

# -*-coding:utf-8 -*-

import unittest
import pandas as pd
from cuffnote.mortgages import Mortgage, ExtraMonthlyPrincipal


class TestExtraMonthlyPrincipal(unittest.TestCase):
    def setUp(self):
        # base mortgage attributes
        self.purhase_price = 200000
        self.down_payment_percent = 0.2
        self.down_payment = self.purhase_price * self.down_payment_percent
        self.loan_amount = self.purhase_price - self.down_payment
        self.interest_rate = 0.03375
        self.start_date = '2021-1-1'
        self.years = 30
        self.num_yearly_pmts = 12
        # instantiate base mortgage
        self.loan = Mortgage(
            self.purhase_price,
            self.down_payment_percent,
            self.interest_rate,
            self.start_date,
            self.years,
            num_yearly_payments=self.num_yearly_pmts
        )
        # extra principal attributes
        self.xtra_principal = 500
        # instantiate mortgage with extra principal
        self.loan_xtra_prncpl = ExtraMonthlyPrincipal(
            self.loan,
            self.xtra_principal
        )
        
    def test_00_get_payment_inheritance(self):
        self.assertEqual(
            self.loan.get_payment(),
            self.loan_xtra_prncpl.get_payment()
        )
        
    def test_01_get_extra_principal(self):
        self.assertEqual(
            self.xtra_principal,
            self.loan_xtra_prncpl.get_extra_principal()
        )
        
    def test_02_set_extra_principal(self):
        self.loan_xtra_prncpl.set_extra_principal(400)
        self.assertEqual(
            400,
            self.loan_xtra_prncpl.get_extra_principal()
        )
        
    def test_03_get_amortization_table_df_instance(self):
        self.assertIsInstance(
            self.loan_xtra_prncpl.get_amortization_table(),
            pd.DataFrame
        )
        
    def test_04_get_amortization_table_extra_principal_col(self):
        self.assertIn(
            'Extra Principal',
            self.loan_xtra_prncpl.get_amortization_table().columns
        )
        
    def test_05_get_amortization_table_equal_extra_principal(self):
        self.assertEqual(
            self.loan_xtra_prncpl.get_extra_principal(),
            self.loan_xtra_prncpl.get_amortization_table().loc[1, 'Extra Principal']
        )
        
    def test_06_set_extra_principal_start_date(self):
        new_start_date = self.loan_xtra_prncpl.get_payment_range()[12].strftime('%Y-%m-%d')
        #self.loan_xtra_prncpl.extra_principal_start_date = new_start_date
        self.loan_xtra_prncpl.set_extra_principal_start_date(new_start_date)
        atable_extra_prncpl_shifted = self.loan_xtra_prncpl.get_amortization_table()
        self.assertEqual(
            0,
            atable_extra_prncpl_shifted.loc[12, 'Extra Principal']
        )
        self.assertEqual(
            self.loan_xtra_prncpl.get_extra_principal(),
            atable_extra_prncpl_shifted.loc[13, 'Extra Principal']
        )
        
    def test_07_get_payoff_date(self):
        # source: https://www.mortgagecalculator.org/calculators/what-if-i-pay-more-calculator.php#top
        # using same inputs, number of periods with monthly extra principal is 167
        num_periods = 167
        self.assertEqual(
            self.loan.get_payment_range()[num_periods-1].strftime('%m-%d-%Y'),
            self.loan_xtra_prncpl.get_payoff_date()
        )
        
    def test_08_get_periods_saved(self):
        periods_saved = 360 - 167
        self.assertEqual(
            periods_saved,
            self.loan_xtra_prncpl.get_periods_saved()
        )
        
    def test_09_get_time_saved(self):
        periods_saved = 360 - 167
        time_saved = f"{periods_saved // self.num_yearly_pmts} years, {periods_saved % self.num_yearly_pmts} months"
        self.assertEqual(
            time_saved,
            self.loan_xtra_prncpl.get_time_saved()
        )
        

if __name__ == '__main__':
    unittest.main()