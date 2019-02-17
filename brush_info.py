import csv
import datetime
import copy
from operator import itemgetter


def get_usage_data(rawdata_file=None, groups_file=None, discard_early=False):

    """
    :return: Brush data in the following structure: {PlaybrushID:
                                                        {weekday:
                                                            {'morning': brush_time,
                                                             'evening': brush_time,
                                                             'brushes': [
                                                                (brush_time, timestamp),...]},
                                                         'group',
                                                         'total_brushes',
                                                         'twice_brushes',
                                                         'avg_brush_time',
                                                         weekday'_brushes',},...
                                                    }
    """

    if not rawdata_file:
        rawdata_file = '1_rawdata.csv'

    if not groups_file:
        groups_file = '2_groups.csv'

    usage_data = {}
    group_data = {}
    with open(rawdata_file, mode='r', encoding='utf-8') as file:
        data = csv.reader(file)
        for row in data:
            if row[0] == '' or row[0] == 'PlaybrushID':
                pass
            else:
                customer_id = row[0]
                weekday = str(row[1][:3]).lower()
                # sums individual brush zone times
                row_total_time = round(sum([float(row[2]),
                                            float(row[3]),
                                            float(row[4]),
                                            float(row[5]),
                                            float(row[6])]), 2)
                timestamp = datetime.datetime.strptime(row[1][:-6], '%a %b %d %Y %H:%M:%S %Z%z')

                if not (discard_early and row_total_time < 20):
                    if customer_id in usage_data:
                        if weekday in usage_data[customer_id]:
                            usage_data[customer_id][weekday]['brushes'].append((row_total_time, timestamp))
                        else:
                            usage_data[customer_id][weekday] = {'brushes': [(row_total_time, timestamp)]}
                    else:
                        usage_data[customer_id] = {weekday: {'brushes': [(row_total_time, timestamp)]}}

    with open(groups_file, mode='r', encoding='utf-8') as file:
        data = csv.reader(file)
        for row in data:
            if row[0] == '' or row[0] == 'group':
                pass
            else:
                group_data[str(row[1])] = str(row[0])

    user_data_copy = copy.deepcopy(usage_data)
    for user_id in user_data_copy:
        total_brushes = 0
        total_brush_duration = 0
        twice_brushes = 0
        for weekday in user_data_copy[user_id]:
            usage_data[user_id][weekday]['brushes'] = consolidate_brushes(usage_data[user_id][weekday]['brushes'])
            brushes_copy = copy.deepcopy(usage_data[user_id][weekday]['brushes'])
            daily_brushes = 0

            for brush in brushes_copy:
                if not discard_early and brush[0] >= 20:
                    if 'morning' not in usage_data[user_id][weekday] and int(brush[1].strftime('%H')) < 14:
                        usage_data[user_id][weekday]['morning'] = brush[0]
                        daily_brushes += 1
                        total_brush_duration += brush[0]
                    elif 'evening' not in usage_data[user_id][weekday] and int(brush[1].strftime('%H')) >= 14:
                        usage_data[user_id][weekday]['evening'] = brush[0]
                        daily_brushes += 1
                        total_brush_duration += brush[0]
                    elif 'morning' in usage_data[user_id][weekday] and 'evening' in usage_data[user_id][weekday]:
                        break

            usage_data[user_id][weekday + '_brushes'] = daily_brushes
            total_brushes += daily_brushes
            if daily_brushes >= 2:
                twice_brushes += 1

        usage_data[user_id]['group'] = group_data.get(user_id, '')
        usage_data[user_id]['total_brushes'] = total_brushes
        usage_data[user_id]['twice_brushes'] = twice_brushes
        try:
            usage_data[user_id]['avg_brush_time'] = total_brush_duration / total_brushes
        except ZeroDivisionError:
            usage_data[user_id]['avg_brush_time'] = 0

    return usage_data


def consolidate_brushes(brushes):
    consolidated_brushes = []
    sorted_brushes = sorted(brushes, key=itemgetter(1))
    beginning_timestamp = datetime.datetime.strptime('Jan 01 1900 00:00:00', '%b %d %Y %H:%M:%S')
    total_brush_time = 0

    for brush in sorted_brushes:
        if len(consolidated_brushes) > 0 and brush[1] <= beginning_timestamp + datetime.timedelta(seconds=120+total_brush_time):
            total_brush_time += brush[0]
            consolidated_brushes[-1] = (total_brush_time, beginning_timestamp)
        else:
            beginning_timestamp = brush[1]
            total_brush_time = brush[0]
            consolidated_brushes.append((total_brush_time, beginning_timestamp))

    return sorted(consolidated_brushes, key=itemgetter(0), reverse=True)


def calculate_group_dynamics(usage_data):
    group_analytics = {}
    group_tuples = []
    for user_id in usage_data:
        if 'group' in usage_data[user_id]:
            group_name = usage_data[user_id]['group']
            if group_name in group_analytics:
                group_analytics[group_name]['user_brush_counts'].append(usage_data[user_id]['total_brushes'])
                group_analytics[group_name]['user_brush_times'].append(usage_data[user_id]['avg_brush_time'])
            else:
                group_analytics[group_name] = {}
                group_analytics[group_name]['user_brush_counts'] = [usage_data[user_id]['total_brushes']]
                group_analytics[group_name]['user_brush_times'] = [usage_data[user_id]['avg_brush_time']]

    for group in group_analytics:
        group_analytics[group]['total_brushes'] = sum(group_analytics[group]['user_brush_counts'])
        try:
            group_analytics[group]['avg_brush_count'] = group_analytics[group]['total_brushes'] \
                                                        / len(group_analytics[group]['user_brush_counts'])
        except ZeroDivisionError:
            group_analytics[group]['avg_brush_count'] = 0

        try:
            group_analytics[group]['avg_brush_time'] = sum(group_analytics[group]['user_brush_times']) \
                                                        / len(group_analytics[group]['user_brush_times'])
        except ZeroDivisionError:
            group_analytics[group]['avg_brush_time'] = 0

        group_tuples.append((group,
                            group_analytics[group]['total_brushes'],
                            group_analytics[group]['avg_brush_count'],
                            group_analytics[group]['avg_brush_time']))

    return group_tuples
    

def write_brush_info_csv(data):
    with open('output.csv', 'w', newline='') as csvfile:
        output = csv.writer(csvfile)
        output.writerow(['group','PBID','mon','tue','wed','thu','fri','sat','sun',
                        'total-brushes','twice-brushes','avg-brush-time'])

        for user_id in data:
            output.writerow([data[user_id].get('group', ''),
                            user_id,
                            data[user_id].get('mon_brushes', 0),
                            data[user_id].get('tue_brushes', 0),
                            data[user_id].get('wed_brushes', 0),
                            data[user_id].get('thu_brushes', 0),
                            data[user_id].get('fri_brushes', 0),
                            data[user_id].get('sat_brushes', 0),
                            data[user_id].get('sun_brushes', 0),
                            data[user_id].get('total_brushes', 0),
                            data[user_id].get('twice_brushes', 0),
                            round(data[user_id].get('avg_brush_time', 0), 2)])


if __name__ == '__main__':
    data = get_usage_data()
    write_brush_info_csv(data)
    print(sorted(calculate_group_dynamics(data), key=itemgetter(3), reverse=True))
    print("all done")
