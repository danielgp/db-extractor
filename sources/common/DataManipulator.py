"""
Data Manipulation class
"""
# package to handle date and times
from datetime import timedelta
# package facilitating Data Frames manipulation
import pandas as pd


class DataManipulator:

    @staticmethod
    def fn_add_days_within_column_to_data_frame(input_data_frame, dict_expression):
        input_data_frame['Days Within'] = input_data_frame[dict_expression['End Date']] - \
                                          input_data_frame[dict_expression['Start Date']] + \
                                          timedelta(days=1)
        input_data_frame['Days Within'] = input_data_frame['Days Within'] \
            .apply(lambda x: int(str(x).replace(' days 00:00:00', '')))
        return input_data_frame

    @staticmethod
    def fn_add_minimum_and_maximum_columns_to_data_frame(input_data_frame, dict_expression):
        grouped_df = input_data_frame.groupby(dict_expression['group_by']) \
            .agg({dict_expression['calculation']: ['min', 'max']})
        grouped_df.columns = ['_'.join(col).strip() for col in grouped_df.columns.values]
        grouped_df = grouped_df.reset_index()
        if 'map' in dict_expression:
            grouped_df.rename(columns=dict_expression['map'], inplace=True)
        return grouped_df

    def fn_add_timeline_evaluation_column_to_data_frame(self, in_df, dict_expression):
        # shorten last method parameter
        de = dict_expression
        # add helpful column to use on "Timeline Evaluation" column determination
        in_df['Reference Date'] = de['Reference Date']
        # actual "Timeline Evaluation" column determination
        cols = ['Reference Date', de['Start Date'], de['End Date']]
        in_df['Timeline Evaluation'] = in_df[cols] \
            .apply(lambda r: 'Current' if r[de['Start Date']]
                                          <= r['Reference Date']
                                          <= r[de['End Date']] else\
                   'Past' if r[de['Start Date']] < r['Reference Date'] else 'Future', axis=1)
        # decide if the helpful column is to be retained or not
        removal_needed = self.fn_decide_by_omission_or_specific_false(de, 'Keep Reference Date')
        if removal_needed:
            in_df.drop(columns=['Reference Date'], inplace=True)
        return in_df

    def add_value_to_dictionary(self, in_list, adding_value, adding_type, reference_column):
        add_type = adding_type.lower()
        total_columns = len(in_list)
        if reference_column is None:
            reference_indexes = {
                'add': {
                    'after': 0,
                    'before': 0,
                },
                'cycle_down_to': {
                    'after': 0,
                    'before': 0,
                },
            }
        else:
            reference_indexes = {
                'add': {
                    'after': in_list.copy().index(reference_column) + 1,
                    'before': in_list.copy().index(reference_column),
                },
                'cycle_down_to': {
                    'after': in_list.copy().index(reference_column),
                    'before': in_list.copy().index(reference_column),
                },
            }
        positions = {
            'after': {
                'cycle_down_to': reference_indexes.get('cycle_down_to').get('after'),
                'add': reference_indexes.get('add').get('after'),
            },
            'before': {
                'cycle_down_to': reference_indexes.get('cycle_down_to').get('before'),
                'add': reference_indexes.get('add').get('before'),
            },
            'first': {
                'cycle_down_to': 0,
                'add': 0,
            },
            'last': {
                'cycle_down_to': total_columns,
                'add': total_columns,
            }
        }
        return self.add_value_to_dictionary_by_position({
            'adding_value': adding_value,
            'list': in_list,
            'position_to_add': positions.get(add_type).get('add'),
            'position_to_cycle_down_to': positions.get(add_type).get('cycle_down_to'),
            'total_columns': total_columns,
        })

    @staticmethod
    def add_value_to_dictionary_by_position(adding_dictionary):
        list_with_values = adding_dictionary['list']
        list_with_values.append(adding_dictionary['total_columns'])
        for counter in range(adding_dictionary['total_columns'],
                             adding_dictionary['position_to_cycle_down_to'], -1):
            list_with_values[counter] = list_with_values[(counter - 1)]
        list_with_values[adding_dictionary['position_to_add']] = adding_dictionary['adding_value']
        return list_with_values

    @staticmethod
    def fn_add_weekday_columns_to_data_frame(input_data_frame, columns_list):
        for current_column in columns_list:
            input_data_frame['Weekday for ' + current_column] = input_data_frame[current_column] \
                .apply(lambda x: x.strftime('%A'))
        return input_data_frame

    @staticmethod
    def fn_apply_query_to_data_frame(local_logger, timmer, input_data_frame, extract_params):
        timmer.start()
        query_expression = ''
        if extract_params['filter_to_apply'] == 'equal':
            local_logger.debug('Will retain only values equal with "'
                               + extract_params['filter_values'] + '" within the field "'
                               + extract_params['column_to_filter'] + '"')
            query_expression = '`' + extract_params['column_to_filter'] + '` == "' \
                               + extract_params['filter_values'] + '"'
        elif extract_params['filter_to_apply'] == 'different':
            local_logger.debug('Will retain only values different than "'
                               + extract_params['filter_values'] + '" within the field "'
                               + extract_params['column_to_filter'] + '"')
            query_expression = '`' + extract_params['column_to_filter'] + '` != "' \
                               + extract_params['filter_values'] + '"'
        elif extract_params['filter_to_apply'] == 'multiple_match':
            local_logger.debug('Will retain only values equal with "'
                               + extract_params['filter_values'] + '" within the field "'
                               + extract_params['column_to_filter'] + '"')
            query_expression = '`' + extract_params['column_to_filter'] + '` in ["' \
                               + '", "'.join(extract_params['filter_values'].values()) \
                               + '"]'
        local_logger.debug('Query expression to apply is: ' + query_expression)
        input_data_frame.query(query_expression, inplace=True)
        timmer.stop()
        return input_data_frame

    @staticmethod
    def fn_convert_datetime_columns_to_string(input_data_frame, columns_list, columns_format):
        for current_column in columns_list:
            input_data_frame[current_column] = \
                input_data_frame[current_column].map(lambda x: x.strftime(columns_format))
        return input_data_frame

    @staticmethod
    def fn_convert_string_columns_to_datetime(input_data_frame, columns_list, columns_format):
        for current_column in columns_list:
            input_data_frame[current_column] = pd.to_datetime(input_data_frame[current_column],
                                                              format=columns_format)
        return input_data_frame

    @staticmethod
    def fn_decide_by_omission_or_specific_false(in_dictionary, key_decision_factor):
        removal_needed = False
        if key_decision_factor not in in_dictionary:
            removal_needed = True
        elif not in_dictionary[key_decision_factor]:
            removal_needed = True
        return removal_needed

    @staticmethod
    def fn_filter_data_frame_by_index(local_logger, in_data_frame, filter_rule):
        index_current = in_data_frame.query('`Timeline Evaluation` == "Current"', inplace=False)
        local_logger.info('Current index has been determined to be ' + str(index_current.index))
        if 'Deviation' in filter_rule:
            for deviation_type in filter_rule['Deviation']:
                deviation_number = filter_rule['Deviation'][deviation_type]
                if deviation_type == 'Lower':
                    index_to_apply = index_current.index - deviation_number
                    in_data_frame = in_data_frame[in_data_frame.index >= index_to_apply[0]]
                elif deviation_type == 'Upper':
                    index_to_apply = index_current.index + deviation_number
                    in_data_frame = in_data_frame[in_data_frame.index <= index_to_apply[0]]
                local_logger.info(deviation_type + ' Deviation Number is ' + str(deviation_number)
                                  + ' to be applied to Current index, became '
                                  + str(index_to_apply))
        return in_data_frame

    @staticmethod
    def get_column_index_from_dataframe(data_frame_columns, column_name_to_identify):
        column_index_to_return = 0
        for ndx, column_name in enumerate(data_frame_columns):
            if column_name == column_name_to_identify:
                column_index_to_return = ndx
        return column_index_to_return

    @staticmethod
    def fn_load_file_list_to_data_frame(local_logger, timmer, file_list, csv_delimiter):
        timmer.start()
        combined_csv = pd.concat([pd.read_csv(filepath_or_buffer=current_file,
                                              delimiter=csv_delimiter,
                                              cache_dates=True,
                                              index_col=None,
                                              memory_map=True,
                                              low_memory=False,
                                              encoding='utf-8',
                                              ) for current_file in file_list])
        local_logger.info('All relevant files were merged into a Pandas Data Frame')
        timmer.stop()
        return combined_csv

    @staticmethod
    def fn_store_data_frame_to_file(local_logger, timmer, input_data_frame, input_file_details):
        timmer.start()
        if input_file_details['format'] == 'csv':
            input_data_frame.to_csv(path_or_buf=input_file_details['name'],
                                    sep=input_file_details['field_delimiter'],
                                    header=True,
                                    index=False,
                                    encoding='utf-8')
        local_logger.info('Data frame has just been saved to file "'
                          + input_file_details['name'] + '"')
        timmer.stop()
