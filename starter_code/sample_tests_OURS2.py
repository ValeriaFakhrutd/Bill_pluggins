"""
CSC148, Winter 2019
Assignment 1
"""
import datetime
import pytest

import json
from typing import List, Dict
from application import create_customers, process_event_history
from customer import Customer
from contract import TermContract, MTMContract, PrepaidContract
from phoneline import PhoneLine
from filter import DurationFilter, CustomerFilter, LocationFilter, ResetFilter

"""
This is a sample test file with a limited set of cases, which are similar in
nature to the full autotesting suite
Use this framework to check some of your work and as a starting point for
creating your own tests
*** Passing these tests does not mean that it will necessarily pass the
autotests ***
"""


def create_single_customer_with_all_lines() -> Customer:
    """ Create a customer with one of each type of PhoneLine
    """
    contracts = [
        TermContract(start=datetime.date(year=2017, month=12, day=25),
                     end=datetime.date(year=2019, month=6, day=25)),
        MTMContract(start=datetime.date(year=2017, month=12, day=25)),
        PrepaidContract(start=datetime.date(year=2017, month=12, day=25),
                        balance=100)
    ]
    numbers = ['867-5309', '273-8255', '649-2568']
    customer = Customer(cid=5555)

    for i in range(len(contracts)):
        customer.add_phone_line(PhoneLine(numbers[i], contracts[i]))

    customer.new_month(12, 2017)
    return customer


test_dict = {'events': [
    {"type": "sms",
     "src_number": "867-5309",
     "dst_number": "273-8255",
     "time": "2018-01-01 01:01:01",
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "sms",
     "src_number": "273-8255",
     "dst_number": "649-2568",
     "time": "2018-01-01 01:01:02",
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "sms",
     "src_number": "649-2568",
     "dst_number": "867-5309",
     "time": "2018-01-01 01:01:03",
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "273-8255",
     "dst_number": "867-5309",
     "time": "2018-01-01 01:01:04",
     "duration": 10,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "867-5309",
     "dst_number": "649-2568",
     "time": "2018-01-01 01:01:05",
     "duration": 50,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]},
    {"type": "call",
     "src_number": "649-2568",
     "dst_number": "273-8255",
     "time": "2018-01-01 01:01:06",
     "duration": 50,
     "src_loc": [-79.42848154284123, 43.641401675960374],
     "dst_loc": [-79.52745693913239, 43.750338501653374]}
    ],
    'customers': [
    {'lines': [
        {'number': '867-5309',
         'contract': 'term'},
        {'number': '273-8255',
         'contract': 'mtm'},
        {'number': '649-2568',
         'contract': 'prepaid'}
    ],
     'id': 5555}
    ]
}


def test_customer_creation() -> None:
    """ Test for the correct creation of Customer, PhoneLine, and Contract
    classes
    """
    customer = create_single_customer_with_all_lines()
    bill = customer.generate_bill(12, 2017)

    assert len(customer.get_phone_numbers()) == 3
    assert len(bill) == 3
    assert bill[0] == 5555
    assert bill[1] == 270.0
    assert len(bill[2]) == 3
    assert bill[2][0]['total'] == 320
    assert bill[2][1]['total'] == 50
    assert bill[2][2]['total'] == -100

    # Check for the customer creation in application.py
    customer = create_customers(test_dict)[0]
    customer.new_month(12, 2017)
    bill = customer.generate_bill(12, 2017)

    assert len(customer.get_phone_numbers()) == 3
    assert len(bill) == 3
    assert bill[0] == 5555
    assert bill[1] == 270.0
    assert len(bill[2]) == 3
    assert bill[2][0]['total'] == 320
    assert bill[2][1]['total'] == 50
    assert bill[2][2]['total'] == -100


def test_events() -> None:
    """ Test the ability to make calls, and ensure that the CallHistory objects
    are populated
    """
    customers = create_customers(test_dict)
    customers[0].new_month(1, 2018)

    process_event_history(test_dict, customers)

    # Check the bill has been computed correctly
    bill = customers[0].generate_bill(1, 2018)
    assert bill[0] == 5555
    assert bill[1] == pytest.approx(-29.925)
    assert bill[2][0]['total'] == pytest.approx(20)
    assert bill[2][0]['free_mins'] == 1
    assert bill[2][1]['total'] == pytest.approx(50.05)
    assert bill[2][1]['billed_mins'] == 1
    assert bill[2][2]['total'] == pytest.approx(-99.975)
    assert bill[2][2]['billed_mins'] == 1

    # Check the CallHistory objects are populated
    history = customers[0].get_call_history('867-5309')
    assert len(history) == 1
    assert len(history[0].incoming_calls) == 1
    assert len(history[0].outgoing_calls) == 1

    history = customers[0].get_call_history()
    assert len(history) == 3
    assert len(history[0].incoming_calls) == 1
    assert len(history[0].outgoing_calls) == 1


def test_contract_start_dates() -> None:
    """ Test the start dates of the contracts.
    Ensure that the start dates are the correct dates as specified in the given
    starter code.
    """
    customers = create_customers(test_dict)
    for c in customers:
        for pl in c._phone_lines:
            assert pl.contract.start == \
                   datetime.date(year=2017, month=12, day=25)
            if hasattr(pl.contract, 'end'):
                # only check if there is an end date (TermContract)
                assert pl.contract.end == \
                       datetime.date(year=2019, month=6, day=25)


def import_data() -> Dict[str, List[Dict]]:
    """ Open the file <dataset.json> which stores the json data, and return
    a dictionary that stores this data in a format as described in the A1
    handout.
    Precondition: the dataset file must be in the json format.
    """
    log = {}
    with open("dataset.json") as o:
        log = json.load(o)
    return log


def test_filters() -> None:
    """ Test the functionality of the filters.
    We are only giving you a couple of tests here, you should expand both the
    dataset and the tests for the different types of applicable filters
    """
    customers = create_customers(test_dict)
    process_event_history(test_dict, customers)

    # Populate the list of calls:
    calls = []
    hist = customers[0].get_history()
    # only consider outgoing calls, we don't want to duplicate calls in the test
    calls.extend(hist[0])

    # The different filters we are testing
    filters = [
        DurationFilter(),
        CustomerFilter(),
        ResetFilter()
    ]

    # These are the inputs to each of the above filters in order.
    # Each list is a test for this input to the filter
    filter_strings = [
        ["L50", "G10", "L0", "50", "AA", ""],
        ["5555", "1111", "9999", "aaaaaaaa", ""],
        ["rrrr", ""]
    ]

    # These are the expected outputs from the above filter application
    # onto the full list of calls
    expected_return_lengths = [
        [1, 2, 0, 3, 3, 3],
        [3, 3, 3, 3, 3],
        [3, 3]
    ]

    for i in range(len(filters)):
        for j in range(len(filter_strings[i])):
            result = filters[i].apply(customers, calls, filter_strings[i][j])
            assert len(result) == expected_return_lengths[i][j]


def test_location_filter_with_large_data() -> None:
    """ Test the functionality of the location filters.
    We are only giving you a couple of tests here, you should expand both the
    dataset and the tests for the different types of applicable filters
    """
    # loading up the large data
    input_dictionary = import_data()
    customers = create_customers(input_dictionary)
    process_event_history(input_dictionary, customers)

    # Populate the list of calls:
    calls = []
    for cust in customers:
        hist = cust.get_history()
        # only look at outgoing calls, we don't want to duplicate calls in test
        calls.extend(hist[0])

    # The different filters we are testing
    filters = [
        CustomerFilter(),
        LocationFilter()

    ]

    # These are the inputs to each of the above filters in order.
    # Each list is a test for this input to the filter
    filter_strings = [
        # contents: non-existent id, valid id, valid id
        ["5555", "5524", "9210"],
        # contents: loc of one call, max and min, one cord out, letters, valid loc but no calls
        ["-79.54717029563305, 43.58020061333403, -79.54717029563303, 43.58020061333405", # location of one call
         "-79.697878, 43.576959, -79.196382, 43.799568", # entire map
         "-80.697877, 43.576960, -79.196383, 43.799567", # one coordinate in not within range
         "hellolol, erferer, fefergerger, ferereeev", # isalpaha == true
         "-79.697878, 43.6882635, -79.196382, 43.799568", # half the map (this one took me hours to count)
         "-79.54717029563305,43.58020061333403,-79.54717029563303,43.58020061333405", # location of one call but no spaces
         "-79.54717029563305  ,   43.58020061333403   ,    -79.54717029563303,   43.58020061333405", # ^ spaces
         "-79.196382, 43.799568, -79.697878, 43.576959",  # both cross
         "-79.296382, 43.576959, -79.597878, 43.799568",  # x coords cross
         "-79.697878, 43.576959, -79.196382, 43.499568",  # y coords cross
         "-80.697877, 69.576960, -89.196383, 69.799567",  # all coords not within range
         "hellolol, erferer, fefergergerferereeev",  # alpha + nums
         "#@%#@%#@%,#%@#%@#%,#%#@%#@%#@$%#@%",  # symbols
         "",  # empty
         "SDF(*@$)(*&#!)(*&#HFLKDSJF:LDSJFLKJDSF",  # no commas
         "                              "  # just spaces.......
         ]
    ]

    # These are the expected outputs from the above filter application
    # onto the full list of calls
    expected_return_lengths = [
        [1000, 45, 33],
        [1, 1000, 1000, 1000, 755, 1000, 1, 1000, 1000, 1000, 1000, 1000, 1000,
         1000, 1000, 1000]
    ]

    for i in range(len(filters)):
        for j in range(len(filter_strings[i])):
            result = filters[i].apply(customers, calls, filter_strings[i][j])
            assert len(result) == expected_return_lengths[i][j]

# updated by gajan feb 17 2019

test_dict_for_term_contract = {'events': [  # ADDED FEB 15 2019
    #  DEC 17 # Start date
    {"type": "call",
     "src_number": "111-1111",
     "dst_number": "444-4444",  # incoming calls dont matter
     "time": "2017-12-01 01:01:04",
     "duration": 9000,  # to make the math easier lol (150 minutes)
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "call",
     "src_number": "222-2222",
     "dst_number": "444-4444",
     "time": "2017-12-01 01:01:05",
     "duration": 9000,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "call",
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2017-12-01 01:01:06",
     "duration": 9000,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},

    {"type": "sms",  # JAN 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-01-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # FEB 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-02-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},

    #  MAR 18 # 111-1111 cancels
    {"type": "call",
     "src_number": "111-1111",
     "dst_number": "444-4444",
     "time": "2018-03-01 01:01:04",
     "duration": 9000,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "call",
     "src_number": "222-2222",
     "dst_number": "444-4444",
     "time": "2018-03-01 01:01:05",
     "duration": 9000,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "call",
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-03-01 01:01:06",
     "duration": 9000,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},

    {"type": "sms",  # APR 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-04-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # MAY 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-05-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # JUN 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-06-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # JUL 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-07-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # AUG 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-08-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # SEPT 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-09-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # OCT 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-10-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # NOV 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-11-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # DEC 18
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2018-12-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # JAN 19
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2019-01-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # FEB 19
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2019-02-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # MAR 19
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2019-03-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # APR 19
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2019-04-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "sms",  # MAY 19
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2019-05-01 01:01:03",
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},

    #  1 JUN 19 i.e. Contract ends
    {"type": "call",
     "src_number": "222-2222",
     "dst_number": "444-4444",
     "time": "2019-06-01 01:01:05",
     "duration": 9000,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "call",
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2019-06-01 01:01:06",
     "duration": 9000,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},

    #  25 JUN 19 # 222-2222 cancels
    {"type": "call",
     "src_number": "222-2222",
     "dst_number": "444-4444",
     "time": "2019-06-25 01:01:05",
     "duration": 9000,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "call",
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2019-06-25 01:01:06",
     "duration": 9000,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},

    #  JUL 2019
    {"type": "call",
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2019-07-01 01:01:06",
     "duration": 3600,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    {"type": "call",
     "src_number": "333-3333",
     "dst_number": "444-4444",
     "time": "2019-07-01 01:01:07",
     "duration": 3600,
     "src_loc": [-79.5, 43.6],
     "dst_loc": [-79.5, 43.6]},
    ],

    'customers': [
    {'lines': [
        {'number': '111-1111',  # cancels before end date
         'contract': 'term'},
        {'number': '222-2222',  # cancels on end date
         'contract': 'term'},
        {'number': '333-3333',  # cancels long after end date
         'contract': 'term'}
    ],
     'id': 5555},
    {'lines': [
        {'number': '444-4444',  # cancels long after end date
         'contract': 'term'}
    ],
     'id': 1111}
    ]
}


def test_term_contract_calculations() -> None:  # ADDED FEB 15 2019
    """ Tests to see if term contracts are correctly computed and there are no
    bugs concerning end dates, cancellations and deposits
    """
    customers = create_customers(test_dict_for_term_contract)
    #  customers[0].new_month(12, 2017)

    process_event_history(test_dict_for_term_contract, customers)

    # Check the bill has been computed correctly
    bill = customers[0].generate_bill(12, 2017)
    assert bill[0] == 5555
    #  assert bill[1] == pytest.approx(975)
    assert bill[2][0]['total'] == pytest.approx(325)
    assert bill[2][0]['free_mins'] == 100
    assert bill[2][0]['billed_mins'] == 50
    assert bill[2][1]['total'] == pytest.approx(325)
    assert bill[2][1]['free_mins'] == 100
    assert bill[2][1]['billed_mins'] == 50
    assert bill[2][2]['total'] == pytest.approx(325)
    assert bill[2][2]['free_mins'] == 100
    assert bill[2][2]['billed_mins'] == 50
    assert bill[1] == pytest.approx(975)

    bill = customers[0].generate_bill(3, 2018)
    assert bill[1] == pytest.approx(75)
    assert bill[2][0]['total'] == pytest.approx(25)
    assert bill[2][1]['total'] == pytest.approx(25)
    assert bill[2][2]['total'] == pytest.approx(25)

    bill = customers[0].generate_bill(6, 2019)
    assert bill[1] == pytest.approx(100)
    assert bill[2][0]['total'] == pytest.approx(20)
    assert bill[2][1]['total'] == pytest.approx(40)
    assert bill[2][2]['total'] == pytest.approx(40)

    bill = customers[0].generate_bill(7, 2019)
    assert bill[1] == pytest.approx(62)
    assert bill[2][0]['total'] == pytest.approx(20)
    assert bill[2][0]['free_mins'] == 0
    assert bill[2][1]['total'] == pytest.approx(20)
    assert bill[2][2]['total'] == pytest.approx(22)
    assert bill[2][2]['free_mins'] == 100
    assert bill[2][2]['billed_mins'] == 20

    assert customers[0]._phone_lines[0].cancel_line() == pytest.approx(-280)
    assert customers[0]._phone_lines[1].cancel_line() == pytest.approx(-280)
    assert customers[0]._phone_lines[2].cancel_line() == pytest.approx(-278)

    # added feb 15 @ 12: 52 pm Kashyap

def test_call_history_one_num_one_cust() -> None:
    """ Test whether choosing one phone number it gives the right amount of
    histories
    """
    # loading up the large data
    input_dictionary = import_data()
    customers = create_customers(input_dictionary)
    process_event_history(input_dictionary, customers)

    # customer id 3852 for number 938-6680
    for cust in customers:
        if cust.get_id() == 3852:
            hist = cust.get_call_history('938-6680')
    total_calls = 0
    for i in hist[0].outgoing_calls:
        total_calls += len(hist[0].outgoing_calls[i])
    for i in hist[0].incoming_calls:
        total_calls += len(hist[0].incoming_calls[i])
    assert total_calls == 17

def test_call_history_all_nums_one_cust() -> None:
    """ Test whether choosing all phone number from one customer it gives the
    right amount of histories
    """
    # loading up the large data
    input_dictionary = import_data()
    customers = create_customers(input_dictionary)
    process_event_history(input_dictionary, customers)

    total_calls = 0
    # customer id 3852 for all their numbers
    for cust in customers:
        if cust.get_id() == 3852:
            hist = cust.get_history()
    total_calls = len(hist[0]) + len((hist[1]))
    assert total_calls == 75
# added by kash feb 16 5 pm

def test_mtm_contract() -> None:
    """ Test whether one number of a customer for mtm is being billed correctly
    """

    # loading up the large data
    input_dictionary = import_data()
    customers = create_customers(input_dictionary)
    process_event_history(input_dictionary, customers)

    for cust in customers:
        if cust.get_id() == 3852:
            customer = cust
            break

    bill = customer.generate_bill(1, 2018)
    assert bill[2][2]['billed_mins'] == 16
    assert bill[2][2]['fixed'] == 50.00
    bill = customer.generate_bill(2, 2018)
    assert bill[2][2]['billed_mins'] == 1
    assert bill[2][2]['fixed'] == 50.00

def test_prepaid_contract() -> None:
    """ Test whether one number of a customer for prepiad is being billed
    correctly
    """

    # loading up the large data
    input_dictionary = import_data()
    customers = create_customers(input_dictionary)
    process_event_history(input_dictionary, customers)

    for cust in customers:
        if cust.get_id() == 3852:
            customer = cust
            break

    bill = customer.generate_bill(1, 2018)
    assert bill[2][-1]['billed_mins'] == 0
    assert bill[2][-1]['fixed'] == -100

def test_all_contract_cancel() -> None:
    """ Test whether one number of a customer for prepiad is being billed
    correctly
    """

    # loading up the large data
    input_dictionary = import_data()
    customers = create_customers(input_dictionary)
    process_event_history(input_dictionary, customers)

    for cust in customers:
        if cust.get_id() == 3852:
            customer = cust
            break

    bill = customer.generate_bill(8, 2018)
    print(bill)
    number = customer.get_phone_numbers()
    print(number)
    # testing if prepaid contract returns 0 when balance < 0
    returned = customer.cancel_phone_line(number[3])
    assert returned == 0
    returned = customer.cancel_phone_line(number[4])
    assert returned == 0
    # testing mtm contract
    returned = customer.cancel_phone_line(number[2])
    assert returned == 50.2
    # testing term contract
    returned = customer.cancel_phone_line(number[0])
    assert returned == 20


if __name__ == '__main__':
    pytest.main(['sample_tests_OURS2.py'])

