"""
--------------------------------
@Time    :  2022/3/4 - 15:39
@Author  :  Lee
@File    :  text
--------------------------------
"""
import pytest
import requests
import allure
from comms.public_api import get_token, replace_data
from comms.constants import DATA_FILE
from comms.log_utils import logger
from comms.db_utils import DBUtils
from comms.excel_utils import ReadExcel


class TestGoods:
    @pytest.fixture(autouse=True)
    def count_db(self):
        self.db = DBUtils()
        yield
        self.db.close()

    cases = ReadExcel.read_data_all(DATA_FILE, 'business_token_goodsinfo')

    @pytest.mark.parametrize('case', cases)
    def test_goods(self, case):
        if '#token#' in case.case_data:
            case.case_data = replace_data(case.case_data, 'token', get_token())

        response = requests.post(url=case.url, data=eval(case.case_data))
        res = response.json()

        try:
            if case.case_id == 1:
                assert case.expect == str(res)
                count_re = len(res['goods_tiems'])
                count_db = self.db.find_count('select * from tb_goods')
                assert count_re == count_db
        except AssertionError as e:
            ReadExcel.write_data(DATA_FILE, 'business_token_goodsinfo', case.case_id, 7, '失败')
            logger.error("测试编号{}，测试标题{}，查询失败！查询结果{}".format(case.case_id, case.case_title, res))
            logger.exception(e)
            raise e
        else:
            ReadExcel.write_data(DATA_FILE, 'business_token_goodsinfo', case.case_id, 7, '成功')
            logger.error("测试编号{}，测试标题{}，查询成功！".format(case.case_id, case.case_title))
