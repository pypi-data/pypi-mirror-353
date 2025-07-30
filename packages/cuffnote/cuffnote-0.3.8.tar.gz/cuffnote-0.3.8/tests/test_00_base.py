#!/usr/bin/env python

# -*-coding:utf-8 -*-

import unittest
import numpy_financial as npf
from datetime import date
import pandas as pd
import numpy as np
from cuffnote.mortgages import Mortgage

class TestBaseMortgage(unittest.TestCase):
    def setUp(self):
        self.purchase_price = 200000
        self.down_payment_percent = 0.2
        self.down_payment = self.purchase_price * self.down_payment_percent
        self.loan_amount = self.purchase_price - self.down_payment
        self.interest_rate = 0.03375
        self.start_date = '2021-1-1'
        self.years = 30
        self.num_yearly_pmts = 12
        self.loan = Mortgage(
            self.purchase_price,
            self.down_payment_percent,
            self.interest_rate,
            self.start_date,
            self.years,
            num_yearly_payments=self.num_yearly_pmts
        )
        
    def test_00_get_payment(self):
        self.assertAlmostEqual(
            self.loan.get_payment(),
            round(-1 * npf.pmt(self.interest_rate/self.num_yearly_pmts, self.num_yearly_pmts*self.years, self.purchase_price - 0.2*self.purchase_price), 2),
            2
        )

    def test_01_get_purchase_price(self):
        self.assertEqual(self.purchase_price, self.loan.get_purchase_price())
        
    def test_02_set_purchase_price(self):
        self.loan.set_purchase_price(250000)
        self.assertEqual(250000, self.loan.get_purchase_price())
        self.assertEqual(0.2*250000, self.loan.get_down_payment())
        self.assertEqual(250000 - (0.2*250000), self.loan.get_loan_amount())
        pmt = round(-1 * npf.pmt(
            self.interest_rate/self.num_yearly_pmts, 
            self.num_yearly_pmts*self.years,
            250000 - 0.2*250000
        ), 2)
        self.assertAlmostEqual(pmt, self.loan.get_payment())

    def test_03_get_down_payment_percent(self):
        self.assertEqual(self.down_payment_percent, self.loan.get_down_payment_percent())
        
    def test_04_set_down_payment_percent(self):
        dpp = 0.25
        self.loan.set_down_payment_percent(dpp)
        self.assertEqual(dpp, self.loan.get_down_payment_percent())
        self.assertEqual(self.purchase_price*dpp, self.loan.get_down_payment())
        self.assertEqual(self.purchase_price - dpp*self.purchase_price, self.loan.get_loan_amount())
        pmt = round(-1 * npf.pmt(
            self.interest_rate/self.num_yearly_pmts,
            self.num_yearly_pmts*self.years,
            self.purchase_price - dpp*self.purchase_price
        ), 2)
        self.assertAlmostEqual(pmt, self.loan.get_payment())

    def test_05_get_down_payment(self):
        self.assertEqual(self.down_payment, self.loan.get_down_payment())
        
    """def test_06_set_down_payment(self):
        dp = 50000
        self.loan.set_down_payment(dp)
        self.assertEqual(dp, self.loan.get_down_payment())
        self.assertEqual(self.purchase_price - dp, self.loan.get_loan_amount())
        self.assertAlmostEqual(dp/self.purchase_price, self.loan.get_down_payment_percent())
        pmt = round(-1 * npf.pmt(
            self.interest_rate/self.num_yearly_pmts,
            self.num_yearly_pmts*self.years,
            self.purchase_price - dp
        ), 2)
        self.assertAlmostEqual(pmt, self.loan.get_payment())"""
        
    def test_07_get_interest_rate(self):
        self.assertEqual(self.interest_rate, self.loan.get_interest_rate())
        
    def test_08_set_interest_rate(self):
        ir = 0.04125
        self.loan.set_interest_rate(ir)
        self.assertEqual(ir, self.loan.get_interest_rate())
        pmt = round(-1 * npf.pmt(
            ir/self.num_yearly_pmts,
            self.num_yearly_pmts*self.years,
            self.loan_amount
        ), 2)
        self.assertAlmostEqual(pmt, self.loan.get_payment())
        
    def test_09_get_years(self):
        self.assertEqual(self.years, self.loan.get_years())
        
    def test_10_set_years(self):
        years = 15
        self.loan.set_years(years)
        self.assertEqual(years, self.loan.get_years())
        pmt = round(-1 * npf.pmt(
            self.interest_rate/self.num_yearly_pmts,
            self.num_yearly_pmts*years,
            self.loan_amount
        ), 2)
        self.assertAlmostEqual(pmt, self.loan.get_payment())
        
    def test_11_get_num_yearly_pmts(self):
        self.assertEqual(self.num_yearly_pmts, self.loan.get_num_yearly_pmts())
        
    def test_12_set_num_yearly_pmts(self):
        num_yearly_pmts = 6
        self.loan.set_num_yearly_pmts(num_yearly_pmts)
        self.assertEqual(num_yearly_pmts, self.loan.get_num_yearly_pmts())
        pmt = round(-1 * npf.pmt(
            self.interest_rate/num_yearly_pmts,
            num_yearly_pmts*self.years,
            self.loan_amount
        ), 2)
        self.assertAlmostEqual(pmt, self.loan.get_payment())
        
    def test_13_get_start_date(self):
        self.assertEqual(self.start_date, self.loan.get_start_date())
        
    def test_14_set_start_date(self):
        start_date = '2022-1-1'
        self.loan.set_start_date(start_date)
        self.assertEqual(start_date, self.loan.get_start_date())
        
    def test_15_get_loan_amount(self):
        self.assertEqual(self.loan_amount, self.loan.get_loan_amount())
        
    def test_16_get_payment_range(self):
        self.assertEqual(self.loan.get_payment_range().dtype, pd.date_range(
            self.start_date, periods=self.years*self.num_yearly_pmts, freq='MS'
        ).dtype)
        self.assertEqual(self.loan.get_payment_range().size, pd.date_range(
            self.start_date, periods=self.years*self.num_yearly_pmts, freq='MS'
        ).size)
        self.assertEqual(
            self.loan.get_payment_range()[0],
            pd.date_range(self.start_date, periods=self.years*self.num_yearly_pmts, freq='MS')[0]
        )
        self.assertEqual(
            self.loan.get_payment_range()[-1],
            pd.date_range(self.start_date, periods=self.years*self.num_yearly_pmts, freq='MS')[-1]
        )
        
    def test_17_get_payoff_date(self):
        self.assertEqual(
            self.loan.get_payoff_date(),
            pd.date_range(self.start_date, periods=self.years*self.num_yearly_pmts, freq='MS')[-1].strftime('%m-%d-%Y')
        )
        
    def test_18_get_number_of_payments(self):
        self.assertEqual(self.years*self.num_yearly_pmts, self.loan.get_number_of_payments())
    
    def test_19_get_amortization_table(self):
        self.assertIsInstance(
            self.loan.get_amortization_table(),
            pd.DataFrame
        )
    
    def test_20_get_total_principal_paid(self):
        self.assertAlmostEqual(
            self.loan_amount,
            self.loan.get_total_principal_paid()
        )
        
    def test_21_get_total_interest_paid(self):
        ipmt = -1 * npf.ipmt(
            self.interest_rate/self.num_yearly_pmts,
            np.arange(self.years*self.num_yearly_pmts) + 1,
            self.years*self.num_yearly_pmts,
            self.loan_amount
        )
        total_ipmt = np.sum(ipmt)
        self.assertAlmostEqual(
            round(total_ipmt, 2),
            self.loan.get_total_interest_paid()
        )
        
    def test_22_get_total_cost_of_loan(self):
        total_principal = self.loan_amount
        ipmt = -1 * npf.ipmt(
            self.interest_rate/self.num_yearly_pmts,
            np.arange(self.years*self.num_yearly_pmts) + 1,
            self.years*self.num_yearly_pmts,
            self.loan_amount
        )
        total_ipmt = np.sum(ipmt)
        total_cost = round(total_principal + total_ipmt, 2)
        self.assertEqual(
            total_cost,
            self.loan.get_total_cost_of_loan()
        )
        
    def test_23_summary_plots(self):
        self.loan.summary_plots()

if __name__ == '__main__':
    unittest.main()