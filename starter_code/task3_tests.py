"""
CSC148, Winter 2019
Assignment 1

Task 1 Tests
"""
import datetime
import pytest
from typing import List, Dict, Union

from application import create_customers, process_event_history
from customer import Customer
from contract import TermContract, MTMContract, PrepaidContract
from phoneline import PhoneLine
from task1_tests import create_customers_log

phone_numbers = ['100-1200', '200-1200', '010-1020', '020-1020',
                 '001-1002', '002-1002', '100-2110', '010-2110',
                 '010-2011', '001-2011', '100-2101', '001-2101',
                 '100-3111', '010-3111', '001-3111']

x1 = -79.572504
x2 = -79.44713
x3 = -79.321756
y1 = 43.743916
y2 = 43.688264
y3 = 43.632611

loc = {1200: (x1, y1), 1020: (x2, y1), 1002: (x3, y1),
       2110: (x1, y2), 2011: (x2, y2), 2101: (x3, y2),
       3111: (x2, y3)}


def create_log() -> Dict[str, List[Dict]]:
    log = {}
    log['events'] = []
    event = {}

    dates = ["2018-11-01", "2018-12-01", "2019-01-01"]

    for i in range(3):
        call_number = 1
        three_calls_only = ['100-1200', '001-2101', '001-3111', '001-2011']
                            #Term, PrePaid, PrePaid
        for src_phone in phone_numbers:
            num_calls = 0
            max_calls = 14
            dur_lst = [[], [], []]
            if src_phone == '100-1200': #Term
                max_calls = 3
                dur_lst = [[20, 30, 40], [50, 10, 40], [50, 60, 40]]
            elif src_phone == '010-1020': #MTM
                for j in range(14):
                    dur_lst[0].append(10 * j)
                    dur_lst[1].append(20 * j)
                    dur_lst[2].append(30 * j)
            elif src_phone == '001-2101': #PrePaid
                max_calls = 3
                dur_lst = [[169, 800, 31], [1000, 931, 69], [500, 469, 531]]
            elif src_phone == '001-3111': #PrePaid
                max_calls = 3
                dur_lst = [[69, 11, 20], [20, 10, 20], [69, 69, 12]]
            elif src_phone == '001-2011': #PrePaid
                max_calls = 3
                dur_lst = [[250, 50, 200], [50, 50, 900], [50, 25, 25]]

            for dst_phone in phone_numbers:
                if src_phone != dst_phone:
                    dur = 60
                    if (src_phone in three_calls_only) and num_calls >= max_calls:
                        break
                    elif src_phone in three_calls_only:
                        dur = dur_lst[i][num_calls] * 60
                        num_calls += 1
                    elif src_phone == '200-1200' or src_phone == '100-2101':
                        dur = 65        #Term
                    elif src_phone == '100-3111':
                        dur = 10 * 60   #Term
                    elif src_phone == '010-1020':
                        dur = dur_lst[i][num_calls] * 60    #MTM
                        num_calls += 1


                    sec = str(call_number % 60)
                    min = str(call_number // 60)
                    if len(sec) == 1:
                        sec = '0' + sec
                    if len(min) == 1:
                        min = '0' + min

                    event['type'] = 'call'
                    event['src_number'] = src_phone
                    event['dst_number'] = dst_phone
                    event['time'] = f'{dates[i]} 01:{min}:{sec}'
                    event['duration'] = dur
                    event['src_loc'] = loc[int(src_phone[4:])]
                    event['dst_loc'] = loc[int(dst_phone[4:])]
                    log['events'].append(event.copy())
                    call_number += 1

    log['customers'] = create_customers_log()
    return log


def create_customers(log: Dict[str, List[Dict]]) -> List[Customer]:
    """ Returns a list of Customer instances for each customer from the input
    dataset from the dictionary <log>.

    Precondition:
    - The <log> dictionary contains the input data in the correct format,
    matching the expected input format described in the handout.
    """
    customer_list = []
    for cust in log['customers']:
        customer = Customer(cust['id'])
        for line in cust['lines']:
            contract = None
            if line['number'] == '100-1200': #Term: Test Free Min
                contract = TermContract(datetime.date(2018, 11, 1), datetime.date(2019, 1, 1))
            elif line['number'] == '200-1200': #Term: Test Cancel After
                contract = TermContract(datetime.date(2018, 11, 1), datetime.date(2018, 12, 1))
            elif line['number'] == '100-2101': #Term: Test Cancel On
                contract = TermContract(datetime.date(2018, 11, 1),
                                        datetime.date(2019, 1, 25))
            elif line['number'] == '100-3111': #Term: Test Cancel Before
                contract = TermContract(datetime.date(2018, 11, 1),
                                        datetime.date(2019, 2, 1))
            elif line['number'] == '001-2101': #Prepaid: positive balance
                contract = PrepaidContract(datetime.date(2018, 11, 1), 25)
            elif line['number'] == '001-3111':  # Prepaid: negative balance
                contract = PrepaidContract(datetime.date(2018, 11, 1), 25)
            elif line['number'] == '001-2011':  # Prepaid: mixed balance
                contract = PrepaidContract(datetime.date(2018, 11, 1), 25)
            elif line['contract'] == 'prepaid':
                # start with $100 credit on the account
                contract = PrepaidContract(datetime.date(2018, 11, 1), 100)
            elif line['contract'] == 'mtm':
                contract = MTMContract(datetime.date(2018, 11, 1))
            elif line['contract'] == 'term':
                contract = TermContract(datetime.date(2018, 11, 1),
                                        datetime.date(2019, 6, 25))
            else:
                print("ERROR: unknown contract type")

            line = PhoneLine(line['number'], contract)
            customer.add_phone_line(line)
        customer_list.append(customer)
    return customer_list


def test_term_contract() -> None:
    log = create_log()
    customers = create_customers(log)
    process_event_history(log, customers)

    for cust in customers:
        if cust.get_id() == 1200:
            for p_line in cust._phone_lines:
                if p_line.number == '100-1200': #Test Free Min
                    bill_summary = p_line.get_bill(11, 2018)
                    assert bill_summary['type'] == 'TERM'
                    assert bill_summary['fixed'] == 320.00
                    assert bill_summary['free_mins'] == 90
                    assert bill_summary['billed_mins'] == 0
                    assert bill_summary['min_rate'] == 0.1
                    assert bill_summary['total'] == 320

                    bill_summary = p_line.get_bill(12, 2018)
                    assert bill_summary['fixed'] == 20.00
                    assert bill_summary['free_mins'] == 100
                    assert bill_summary['billed_mins'] == 0
                    assert bill_summary['total'] == 20.00

                    bill_summary = p_line.get_bill(1, 2019)
                    assert bill_summary['type'] == 'TERM'
                    assert bill_summary['fixed'] == 20.00
                    assert bill_summary['free_mins'] == 100
                    assert bill_summary['billed_mins'] == 50
                    assert bill_summary['min_rate'] == 0.1
                    assert bill_summary['total'] == 25.00
            #Test Cancel After
            for line in cust._phone_lines:
                if line.number == '200-1200':
                    assert cust.cancel_phone_line(line.number) == -280
                    break
        elif cust.get_id() == 2101:
            # Test Cancel On
            for line in cust._phone_lines:
                if line.number == '100-2101':
                    assert cust.cancel_phone_line(line.number) == 20
                    break
        elif cust.get_id() == 3111:
            # Test Cancel Before
            for line in cust._phone_lines:
                if line.number == '100-3111':
                    assert cust.cancel_phone_line(line.number) == 24
                    break


def test_mtm_contract() -> None:
    log = create_log()
    customers = create_customers(log)
    process_event_history(log, customers)

    for cust in customers:
        if cust.get_id() == 1020:
            for p_line in cust._phone_lines:
                if p_line.number == '010-1020': #Test different number of cals
                    bill_summary = p_line.get_bill(11, 2018)
                    assert bill_summary['type'] == 'MTM'
                    assert bill_summary['billed_mins'] == 910
                    assert bill_summary['min_rate'] == 0.05
                    assert bill_summary['total'] == 95.5

                    bill_summary = p_line.get_bill(12, 2018)
                    assert bill_summary['type'] == 'MTM'
                    assert bill_summary['billed_mins'] == 1820
                    assert bill_summary['min_rate'] == 0.05
                    assert bill_summary['total'] == 141

                    bill_summary = p_line.get_bill(1, 2019)
                    assert bill_summary['type'] == 'MTM'
                    assert bill_summary['billed_mins'] == 2730
                    assert bill_summary['min_rate'] == 0.05
                    assert bill_summary['total'] == 186.5


def test_prepaid_contract() -> None:
    log = create_log()
    customers = create_customers(log)
    process_event_history(log, customers)

    for cust in customers:
        if cust.get_id() == 2101:
            for p_line in cust._phone_lines:
                if p_line.number == '001-2101': #Test different starting balance
                    bill_summary = p_line.get_bill(11, 2018)
                    assert bill_summary['type'] == 'PREPAID'
                    assert bill_summary['billed_mins'] == 1000
                    assert bill_summary['min_rate'] == 0.025
                    assert bill_summary['total'] == 0

                    bill_summary = p_line.get_bill(12, 2018)
                    assert bill_summary['type'] == 'PREPAID'
                    assert bill_summary['billed_mins'] == 2000
                    assert bill_summary['min_rate'] == 0.025
                    assert bill_summary['total'] == 25

                    bill_summary = p_line.get_bill(1, 2019)
                    assert bill_summary['type'] == 'PREPAID'
                    assert bill_summary['billed_mins'] == 1500
                    assert bill_summary['min_rate'] == 0.025
                    assert bill_summary['total'] == 37.5

        elif cust.get_id() == 3011:
            for p_line in cust._phone_lines:
                if p_line.number == '001-3111': #Test different starting balance
                    bill_summary = p_line.get_bill(11, 2018)
                    assert bill_summary['type'] == 'PREPAID'
                    assert bill_summary['billed_mins'] == 100
                    assert bill_summary['min_rate'] == 0.025
                    assert bill_summary['total'] == -22.5
                    assert bill_summary['free_mins'] == 0

                    bill_summary = p_line.get_bill(12, 2019)
                    assert bill_summary['type'] == 'PREPAID'
                    assert bill_summary['billed_mins'] == 50
                    assert bill_summary['min_rate'] == 0.025
                    assert bill_summary['total'] == -21.25
                    assert bill_summary['free_mins'] == 0

                    bill_summary = p_line.get_bill(1, 2019)
                    assert bill_summary['type'] == 'PREPAID'
                    assert bill_summary['billed_mins'] == 150
                    assert bill_summary['min_rate'] == 0.025
                    assert bill_summary['total'] == -17.5
                    assert bill_summary['free_mins'] == 0


def test_monthly_bill() -> None:
    log = create_log()
    customers = create_customers(log)
    process_event_history(log, customers)

    for cust in customers:
        if cust.get_id() == 1200:
            assert cust.generate_bill(11, 2018)[1] == 320 + 320
            assert cust.generate_bill(12, 2018)[1] == 20 + 20
            assert cust.generate_bill(1, 2019)[1] == 25 + 20
        elif cust.get_id == 1020:
            assert cust.generate_bill(11, 2018)[1] == 95.5 + 50.7
            assert cust.generate_bill(12, 2018)[1] == 141 + 50.7
            assert cust.generate_bill(1, 2019)[1] == 186.5 + 50.7
        elif cust.get_id == 1002:
            assert cust.generate_bill(11, 2018)[1] == 2*-99.65
            assert cust.generate_bill(12, 2018)[1] == 2*-99.3
            assert cust.generate_bill(1, 2019)[1] == 2*-98.95
        elif cust.get_id == 2110:
            assert cust.generate_bill(11, 2018)[1] == 320*2
            assert cust.generate_bill(12, 2018)[1] == 20*2
            assert cust.generate_bill(1, 2019)[1] == 20*2
        elif cust.get_id == 2101:
            assert cust.generate_bill(11, 2018)[1] == 320
            assert cust.generate_bill(12, 2018)[1] == 20 + 25
            assert cust.generate_bill(1, 2019)[1] == 20 + 37.5
        elif cust.get_id == 2011:
            assert cust.generate_bill(11, 2018)[1] == 50.7 - 12.5
            assert cust.generate_bill(12, 2018)[1] == 50.7 + 12.5
            assert cust.generate_bill(1, 2019)[1] == 50.7 - 10
        elif cust.get_id == 3111:
            assert cust.generate_bill(11, 2018)[1] == 324 + 50.7 - 22.5
            assert cust.generate_bill(12, 2018)[1] == 24 + 50.7 - 21.25
            assert cust.generate_bill(1, 2019)[1] == 24 + 50.7 - 17.5


if __name__ == '__main__':
    pytest.main(['task3_tests.py'])

