from StringUtil import  StringUtil


class Player(object):
    @staticmethod
    def parse_height_to_get_inches(val: str):
        """
        Parses height and returns number of inches
        :param val: Expected input: ' 6\'1"'
        :type val:
        :return:
        :rtype:
        """
        if not val:
            return

        try:
            val = val.strip()

            values = val.split('\'')
            feet = StringUtil.remove_everything_but_numbers(values[0].strip())
            inches = StringUtil.remove_everything_but_numbers(values[1].strip())

            return (12 * feet) + inches
        except:
            return None

    @staticmethod
    def parse_cost(val: str):
        if not val:
            return

        from StringUtil import StringUtil

        val = str(val).lower()

        number_to_multiple_by = 1

        if 'k' in val:
            number_to_multiple_by = 1000
        if 'm' in val:
            number_to_multiple_by = 1000000


        num_val = StringUtil.remove_everything_but_decimals(val)

        return num_val * number_to_multiple_by