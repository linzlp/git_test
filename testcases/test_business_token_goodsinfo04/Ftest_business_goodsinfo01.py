"""
--------------------------------
@Time    :  2022/3/4 - 14:02
@Author  :  Lee
@File    :  test_business_goodsinfo01
--------------------------------
"""
import pytest
import requests
from comms.constants import DATA_FILE
from comms.log_utils import logger
from comms.excel_utils import ReadExcel
from comms.public_api import get_token, replace_data

"""
1.主流程
"""


class TestGoodsInfo:
    cases = ReadExcel.read_data_pl(DATA_FILE, "business_token_goodsinfo", 1, 1)

    @pytest.mark.parametrize('case', cases)
    def test_goods_info(self, case):
        if '#token#' in case.case_data:
            case.case_data = replace_data(case.case_data, 'token', get_token())

        response = requests.post(url=case.url, data=eval(case.case_data))
        res = response.json()

        try:
            assert case.expect in str(res)
        except AssertionError as e:
            ReadExcel.write_data(DATA_FILE, 'business_token_goodsinfo', case.case_id, 7, '失败')
            logger.error("测试编号{}，测试标题{}，测试失败！实际结果{}".format(case.case_id, case.case_title, res))
            logger.exception(e)
            raise e
        else:
            ReadExcel.write_data(DATA_FILE, 'business_token_goodsinfo', case.case_id, 7, '成功')
            logger.info('测试编号{}，测试标题{}，测试成功！'.format(case.case_id, case.case_title))


if __name__ == '__main__':
    pytest.main(['-vs', './Ftest_business_goodsinfo01.py'])
