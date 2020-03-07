"""
CSC148, Winter 2019
Assignment 1

Task 1 Tests
"""
import datetime
import pytest
from typing import List, Dict, Union

from application import create_customers, process_event_history
from visualizer import Visualizer
from task1_tests import create_customers_log, create_pure_log
from filter import CustomerFilter, DurationFilter, LocationFilter

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

def create_task4_log() -> Dict[str, List[Dict]]:
    log = {}
    log['events'] = []
    event = {}

    dates = ["2018-11-01", "2018-12-01", "2019-01-01"]

    for i in range(3):
        call_number = 1
        three_calls_only = ['100-1200', '001-2101', '001-3111']
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


def test_customer_filter() -> None:
    log = create_pure_log()
    customers = create_customers(log)
    process_event_history(log, customers)
    all_calls = []
    for c in customers:
        hist = c.get_history()
        all_calls.extend(hist[0])

    fil = CustomerFilter()
    invalid_inputs = ['', 'dskljgdf', '69.69', 'd1200', 'L200',
                      '-79.6, 43.3, -79.5, 43.4', '3690', ' ']
    for input in invalid_inputs:
        filtered = fil.apply(customers, all_calls, input)
        assert filtered == all_calls

    line_of_customer = ['100-2101', '001-2101']
    filtered = fil.apply(customers, all_calls, '2101')
    for call in filtered:
        assert call.src_number in line_of_customer \
               or call.dst_number in line_of_customer
        assert loc[2101] == call.src_loc or loc[2101] == call.dst_loc


def test_duration_filter() -> None:
    log = create_task4_log()
    customers = create_customers(log)
    process_event_history(log, customers)

    all_calls = []
    for c in customers:
        hist = c.get_history()
        all_calls.extend(hist[0])

    fil = DurationFilter()
    invalid_inputs = ['', 'LG40', 'l50', 'g65', '50', 'sdklfjeind', ' ']
    for input in invalid_inputs:
        filtered = fil.apply(customers, all_calls, input)
        assert filtered == all_calls

    filtered = fil.apply(customers, all_calls, 'L60')
    for call in filtered:
         assert call.duration < 60

    filtered = fil.apply(customers, filtered, 'G60')
    assert filtered == []

    filtered = fil.apply(customers, all_calls, 'G5400')
    for call in filtered:
        assert call.duration > 5400


def test_location_filter() -> None:
    log = create_pure_log()
    customers = create_customers(log)
    process_event_history(log, customers)
    all_calls = []
    for c in customers:
        hist = c.get_history()
        all_calls.extend(hist[0])

    rx = (x2 - x1) / 4
    ry = (y1 - y2) / 4

    fil = LocationFilter()
    MIN_LONGITUDE = -79.697878
    MAX_LONGITUDE = -79.196382
    MIN_LATITUDE = 43.576959
    MAX_LATITUDE = 43.799568
    invalid_inputs = ['', f'{MIN_LONGITUDE}, {MIN_LATITUDE},{MAX_LONGITUDE},{MAX_LATITUDE}',
                      f'-79.698, {MIN_LATITUDE}, {MAX_LONGITUDE}, {MAX_LATITUDE}',
                      f'{MIN_LONGITUDE}, 43.576, {MAX_LONGITUDE}, {MAX_LATITUDE}',
                      f'{MIN_LONGITUDE}, {MIN_LATITUDE}, -79.195, {MAX_LATITUDE}',
                      f'{MIN_LONGITUDE}, {MIN_LATITUDE}, {MAX_LONGITUDE}, 43.8',
                      f'{MIN_LONGITUDE},{MIN_LATITUDE}, -79.54, {MAX_LATITUDE}',
                      f'{MIN_LONGITUDE}, {MIN_LATITUDE}, {MAX_LATITUDE}',
                      f'-79.6, 43.60, -79.2, 43.75, -79.5',
                      'klsjdfohg[we', ' ']

    for input in invalid_inputs:
        filtered = fil.apply(customers, all_calls, input)
        assert filtered == all_calls

    for key in loc.keys():
        x = loc[key][0]
        y = loc[key][1]
        fil_string = f'{x - rx}, {y - ry}, {x + rx}, {y + ry}'
        filtered = fil.apply(customers, all_calls, fil_string)
        lines_in_area = []
        if key == 3111:
            assert len(filtered) == (24 * 3 + 6) * 3
        else:
            assert len(filtered) == 27 * 2 * 3
        for cust in customers:
            if cust.get_id() == key:
                lines_in_area = cust.get_phone_numbers()
                break

        for call in filtered:
            assert call.src_number in lines_in_area \
                    or call.dst_number in lines_in_area
            assert loc[int(call.src_number[4:])] == call.src_loc \
                    or loc[int(call.dst_number[4:])] == call.dst_loc

    fil_string = f'{x1 - rx}, {y2 - ry}, {x1 + rx}, {y1 + ry}'
    filtered = fil.apply(customers, all_calls, fil_string)
    lines_in_area = ['100-1200', '200-1200', '100-2110', '010-2110']
    assert len(filtered) == (11 * 4 * 2 + 12) * 3
    for call in filtered:
        assert call.src_number in lines_in_area \
               or call.dst_number in lines_in_area
        assert loc[int(call.src_number[4:])] == call.src_loc \
               or loc[int(call.dst_number[4:])] == call.dst_loc

    fil_string = f'{x1}, {y2}, {x2}, {y1}'
    filtered = fil.apply(customers, all_calls, fil_string)
    lines_in_area = ['100-1200', '200-1200', '100-2110', '010-2110',
                     '010-1020', '020-1020', '010-2011', '001-2011']
    assert len(filtered) == (7 * 8 * 3) * 3
    for call in filtered:
        assert call.src_number in lines_in_area \
               or call.dst_number in lines_in_area
        assert loc[int(call.src_number[4:])] == call.src_loc \
               or loc[int(call.dst_number[4:])] == call.dst_loc


def test_combined_filters() -> None:
    log = create_task4_log()
    customers = create_customers(log)
    process_event_history(log, customers)
    all_calls = []
    for c in customers:
        hist = c.get_history()
        all_calls.extend(hist[0])

    fil = LocationFilter()
    filtered = fil.apply(customers, all_calls, f'{x2}, {y3}, {x2}, {y3}')
    fil = DurationFilter()
    filtered = fil.apply(customers, filtered, f'G{69 * 60 - 1}')
    filtered = fil.apply(customers, filtered, f'L{69 * 60 + 1}')
    assert len(filtered) == 3
    count = 0
    for call in filtered:
        assert call.src_number == '001-3111'
        if call.time.month == 1:
            count += 1
    assert count == 2

    fil = CustomerFilter()
    filtered = fil.apply(customers, all_calls, "1020")
    fil = DurationFilter()
    filtered = fil.apply(customers, filtered, f'G{10 * 60 - 1}')
    filtered = fil.apply(customers, filtered, f'L{130 * 60 + 1}')
    for call in filtered:
        assert 10 * 60 - 1 < call.duration < 130 * 60 + 1
        print(f'src: {call.src_number}, dst: {call.dst_number}, dur: {call.duration}')
    assert len(filtered) == 23 + 11 + 6

    fil = LocationFilter()
    filtered = fil.apply(customers, all_calls, f'{x3}, {y2}, {x3}, {y2}') #2101
    fil = CustomerFilter()
    filtered = fil.apply(customers, filtered, "1002")
    assert len(filtered) == 3 * 2 * 3
    for call in filtered:
        assert call.src_number[4:] == '1002' or call.src_number[4:] == '2101'
    assert fil.apply(customers, filtered, "3111") == []
    fil = DurationFilter()
    assert fil.apply(customers, filtered, 'L60') == []


if __name__ == '__main__':
    pytest.main(['task4_tests.py'])

    v = Visualizer()
    print("Toronto map coordinates:")
    print("  Lower-left corner: -79.697878, 43.576959")
    print("  Upper-right corner: -79.196382, 43.799568")

    log = create_task4_log()
    customers = create_customers(log)
    process_event_history(log, customers)

    # ----------------------------------------------------------------------
    # NOTE: You do not need to understand any of the implementation below,
    # to be able to solve this assignment. However, feel free to
    # read it anyway, just to get a sense of how the application runs.
    # ----------------------------------------------------------------------

    # Gather all calls to be drawn on screen for filtering, but we only want
    # to plot each call only once, so only plot the outgoing calls to screen.
    # (Each call is registered as both an incoming and outgoing)
    all_calls = []
    for c in customers:
        hist = c.get_history()
        all_calls.extend(hist[0])
    print("\n-----------------------------------------")
    print("Total Calls in the dataset:", len(all_calls))

    # Main loop for the application.
    # 1) Wait for user interaction with the system and processes everything
    #    appropriately
    # 2) Take the calls from the results of the filtering and create the
    #    drawables and connection lines for those calls
    # 3) Display the calls in the visualization window
    events = all_calls
    while not v.has_quit():
        events = v.handle_window_events(customers, events)

        connections = []
        drawables = []
        for event in events:
            connections.append(event.get_connection())
            drawables.extend(event.get_drawables())

        # Put the connections on top of the other sprites
        drawables.extend(connections)
        v.render_drawables(drawables)


