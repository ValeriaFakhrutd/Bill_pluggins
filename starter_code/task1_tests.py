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

def create_pure_log() -> Dict[str, List[Dict]]:
    log = {}
    log['events'] = []
    event = {}
    # start_time

    lst = []
    m1 = {}
    m2 = {}
    m3 = {}
    lst.append(m1)
    lst.append(m2)
    lst.append(m3)

    dates = ["2018-11-01", "2018-12-01", "2019-01-01"]
    for i in range(3):
        call_number = 1
        for src_phone in phone_numbers:
            for dst_phone in phone_numbers:

                # if (src_phone, dst_phone) in lst[i]
                if src_phone != dst_phone:
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
                    event['duration'] = 100         #lst[i][(src_phone, dst_phone)]
                    event['src_loc'] = loc[int(src_phone[4:])]
                    event['dst_loc'] = loc[int(dst_phone[4:])]
                    log['events'].append(event.copy())
                    call_number += 1

    log['customers'] = create_customers_log()
    return log


def create_log() -> Dict[str, List[Dict]]:
    log = {}
    log['events'] = []
    event = {}
    dates = ["2018-11-01", "2018-12-01", "2019-01-01"]

    for i in range(len(dates)):
        call_number = 1
        for src_phone in phone_numbers:
            for dst_phone in phone_numbers:
                if src_phone != dst_phone:
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
                    event['duration'] = 60
                    event['src_loc'] = loc[int(src_phone[4:])]
                    event['dst_loc'] = loc[int(dst_phone[4:])]
                    log['events'].append(event.copy())
                    call_number += 1

    log['customers'] = create_customers_log()
    return log


def create_customers_log() -> List[Dict[str, Dict[str, Union[int, str]]]]:
    customer_log = []
    nums = []
    cur_id = 1200
    for line in phone_numbers:
        c_id = line[4:]
        if int(c_id) != cur_id or line == '001-3111':
            if line == '001-3111':
                nums.append(line)
            customer = {}
            lines = []
            dic = {}
            for num in nums:
                dic['number'] = num
                if int(num[0]) != 0:
                    dic['contract'] = 'term'
                elif int(num[1]) != 0:
                    dic['contract'] = 'mtm'
                else:
                    dic['contract'] = 'prepaid'
                lines.append(dic.copy())

            customer['lines'] = lines.copy()
            customer['id'] = cur_id
            customer_log.append(customer.copy())
            cur_id = int(c_id)
            nums = [line]
        else:
            nums.append(line)

    return customer_log

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
            if line['contract'] == 'prepaid':
                # start with $100 credit on the account
                contract = PrepaidContract(datetime.date(2018, 11, 1), 100)
            elif line['contract'] == 'mtm':
                contract = MTMContract(datetime.date(2018, 12, 1))
            elif line['contract'] == 'term':
                contract = TermContract(datetime.date(2018, 12, 1),
                                        datetime.date(2019, 6, 25))
            else:
                print("ERROR: unknown contract type")

            line = PhoneLine(line['number'], contract)
            customer.add_phone_line(line)
        customer_list.append(customer)
    return customer_list


def test_customer_creation() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """
    log = create_pure_log()
    customers = create_customers(log)

    for line in phone_numbers:
        one_customer_with = False
        for cust in customers:
            for p_line in cust._phone_lines:
                num = p_line.number
                if (num[0] == 1 or num[0] == 2) and num[1] == 0 and num[2] == 0:
                    assert isinstance(p_line.contract, TermContract)
                elif num[0] ==0 and (num[1] == 1 or num[1] == 2) and num[2] == 0:
                    assert isinstance(p_line.contract, MTMContract)
                elif num[0] == 0 and num[1] == 0 and (num[2] == 1 or num[2] == 2):
                    assert isinstance(p_line.contract, PrepaidContract)
                else:
                    assert True

            if line in cust:
                one_customer_with = True
                assert cust.get_id() == int(line[4:])
                if cust.get_id() == 3111:
                    assert len(cust._phone_lines) == 3
                else:
                    assert len(cust._phone_lines) == 2
        assert one_customer_with


def test_events_pure_calls() -> None:
    log = create_pure_log()
    customers = create_customers(log)

    process_event_history(log, customers)
    for cust in customers:
        if cust.get_id() == 3111:
            assert len(cust.get_history()[0]) == 126
        else:
            assert len(cust.get_history()[0]) == 84

        for p_line in cust._phone_lines:
            m1_history = p_line.callhistory.get_monthly_history(11, 2018)
            assert len(m1_history[0]) == 14
            assert len(m1_history[1]) == 14
            for out_call in m1_history[0]:
                assert out_call.src_loc == loc[int(out_call.src_number[4:])]
            for in_call in m1_history[1]:
                assert in_call.dst_loc == loc[int(in_call.dst_number[4:])]

            m2_history = p_line.callhistory.get_monthly_history(12, 2018)
            assert len(m2_history[0]) == 14
            assert len(m2_history[1]) == 14
            for out_call in m2_history[0]:
                assert out_call.src_loc == loc[int(out_call.src_number[4:])]
            for in_call in m2_history[1]:
                assert in_call.dst_loc == loc[int(in_call.dst_number[4:])]

            m3_history = p_line.callhistory.get_monthly_history(1, 2019)
            assert len(m3_history[0]) == 14
            assert len(m3_history[1]) == 14
            for out_call in m3_history[0]:
                assert out_call.src_loc == loc[int(out_call.src_number[4:])]
            for in_call in m3_history[1]:
                assert in_call.dst_loc == loc[int(in_call.dst_number[4:])]


if __name__ == '__main__':
    pytest.main(['task1_tests.py'])

