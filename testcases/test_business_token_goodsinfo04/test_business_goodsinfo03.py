"""
--------------------------------
@Time    :  2022/3/4 - 14:02
@Author  :  Lee
@File    :  test_business_goodsinfo01
--------------------------------
"""
import pytest
import requests
import allure
from comms.constants import DATA_FILE
from comms.log_utils import logger
from comms.excel_utils import ReadExcel
from comms.public_api import get_token, replace_data
from comms.db_utils import DBUtils

"""
1.主流程
2.数据回滚和数据验证
3.追加其他case和allure
"""


@allure.feature("商品查询模块")
class TestGoodsInfo:

    @pytest.fixture(autouse=True)
    def connect_db(self):
        self.db = DBUtils()
        yield
        self.db.close()

    cases = ReadExcel.read_data_all(DATA_FILE, "business_token_goodsinfo")

    @allure.severity('critical')
    @allure.description("商品查询模块测试案例")
    @pytest.mark.parametrize('case', cases)
    def test_goods_info(self, case):
        allure.dynamic.title(case.case_title)
        allure.attach(body=case.url, name='商品路径')
        allure.attach(body=case.case_data, name="商品参数")

        if '#token#' in case.case_data:
            case.case_data = replace_data(case.case_data, 'token', get_token())
            if case.case_id == 3:  # token区分大小写的场景
                case.case_data = replace_data(case.case_data, 'token', get_token().upper())
            if case.case_data == 4:
                token = get_token()
                get_token()
                case.case_data = replace_data(case.case_data, 'token', token)

        response = requests.post(url=case.url, data=eval(case.case_data))
        res = response.json()
        allure.attach(body=str(res), name='响应结果')

        try:
            if case.case_id == 1:
                assert case.expect in str(res)  # 判断响应体包含  查询成功
                # 判断查询商品条目数是否正确
                # 1.获取返回的结果条目数
                res_count = len(res["goods_tiems"])
                # 2.获取数据库的商品条目数
                db_count = self.db.find_count('select * from tb_goods;')
                assert res_count == db_count  # 响应体的商品条目数和数据库的商品条目数做对比
            elif case.case_id in (5, 6):
                assert case.expect in str(res)  # 判断响应体包含 查询成功
                res_count = len(res["goods_tiems"])
                db_count = self.db.find_count('select * from tb_goods where isOnSale = %s;',
                                              (eval(case.case_data)["isOnSale"],))
                assert res_count == db_count  # 响应体的商品条目数和数据库的商品条目数做对比
            elif case.case_id in (7, 8):
                assert case.expect in str(res)  # 判断响应体包含 查询成功
                res_count = len(res["goods_tiems"])
                db_count = self.db.find_count('select * from tb_goods where isPromote = %s;',
                                              (eval(case.case_data)["isPromote"],))
                assert res_count == db_count  # 响应体的商品条目数和数据库的商品条目数做对比
            elif case.case_id in (9, 10, 11, 12):
                assert case.expect in str(res)  # 判断响应体包含 查询成功
                res_count = len(res["goods_tiems"])
                db_count = self.db.find_count('select * from tb_goods where isPromote = %s and isOnSale = %s;',
                                              (eval(case.case_data)["isPromote"], eval(case.case_data)["isOnSale"]))
                assert res_count == db_count  # 响应体的商品条目数和数据库的商品条目数做对比
            elif case.case_id in (13, 14, 15, 16, 17, 18, 19, 20, 23):
                assert case.expect in str(res)  # 判断响应体包含 查询成功
                res_count = len(res["goods_tiems"])
                assert res_count == 1
            else:
                assert eval(case.expect) == res

        except AssertionError as e:
            ReadExcel.write_data(DATA_FILE, 'business_token_goodsinfo', case.case_id, 7, '失败')
            logger.error("测试编号{}，测试标题{}，测试失败！实际结果{}".format(case.case_id, case.case_title, res))
            logger.exception(e)
            raise e
        else:
            ReadExcel.write_data(DATA_FILE, 'business_token_goodsinfo', case.case_id, 7, '成功')
        logger.info('测试编号{}，测试标题{}，测试成功！'.format(case.case_id, case.case_title))


if __name__ == '__main__':
    pytest.main(['-vs', './test_business_goodsinfo03.py'])
