
# standard Python packages
from datetime import datetime as ClassDT
from datetime import timedelta

# Custom classes specific to this package
from sources.data_extractor.BasicNeeds import BasicNeeds


class ParameterHandling:
    lcl_c_bn = None

    def __init__(self):
        self.lcl_c_bn = BasicNeeds()

    def build_parameters(self, local_logger, query_session_parameters, in_parameter_rules):
        local_logger.debug('Seen Parameters are: ' + str(query_session_parameters))
        parameters_type = type(query_session_parameters)
        local_logger.debug('Parameters type is ' + str(parameters_type))
        if str(parameters_type) == "<class 'dict'>":
            tp = tuple(query_session_parameters.values())
        elif str(parameters_type) == "<class 'list'>":
            tp = tuple(query_session_parameters)
        else:
            local_logger.error('Unknown parameter type (expected either Dictionary or List)')
            exit(1)
        local_logger.debug('Initial Tuple for Parameters is: ' + str(tp))
        return self.stringify_parameters(local_logger, tp, in_parameter_rules)

    def calculate_date_from_expression(self, local_logger, expression_parts):
        final_string = ''
        current_date = ClassDT.today()
        if expression_parts[1] == 'CYCW':
            if len(expression_parts) >= 3:
                current_date = current_date + timedelta(weeks=int(expression_parts[2]))
            week_iso_num = ClassDT.isocalendar(current_date)[1]
            final_string = str(ClassDT.isocalendar(current_date)[0])\
                           + self.lcl_c_bn.fn_numbers_with_leading_zero(str(week_iso_num), 2)
        else:
            local_logger.error('Unknown expression encountered '
                               + str(expression_parts[1]) + '...')
            exit(1)
        return final_string

    def stringify_parameters(self, local_logger, tuple_parameters, given_parameter_rules):
        working_list = []
        for ndx, crt_parameter in enumerate(tuple_parameters):
            current_parameter_type = str(type(crt_parameter))
            working_list.append(ndx)
            if current_parameter_type == "<class 'str'>":
                local_logger.debug('Current Parameter is STR and has the value: ' + crt_parameter)
                if len(crt_parameter) > 14 and crt_parameter[:15] == 'CalculatedDate_':
                    parameter_value_parts = crt_parameter.split('_')
                    crt_parameter = self.calculate_date_from_expression(local_logger,
                                                                        parameter_value_parts)
                    local_logger.debug('Current Parameter is STR '
                                       + 'and has been re-interpreted as value: '
                                       + str(crt_parameter))
                working_list[ndx] = crt_parameter
            elif current_parameter_type == "<class 'list'>":
                local_logger.debug('Current Parameter is LIST and has the value: '
                                   + str(crt_parameter))
                working_list[ndx] = given_parameter_rules['list-values-prefix'] \
                                    + given_parameter_rules['list-values-glue']\
                                        .join(crt_parameter) \
                                    + given_parameter_rules['list-values-suffix']
            elif current_parameter_type == "<class 'dict'>":
                local_logger.debug('Current Parameter is DICT and has the value: '
                                   + str(crt_parameter))
                working_list[ndx] = given_parameter_rules['dictionary-values-prefix'] \
                                    + given_parameter_rules['dictionary-values-glue']\
                                        .join(crt_parameter.values()) \
                                    + given_parameter_rules['dictionary-values-suffix']
        final_tuple = tuple(working_list)
        local_logger.debug('Final Tuple for Parameters is: ' + str(final_tuple))
        return final_tuple
