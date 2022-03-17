"""
--------------------------------
@Time    :  2022/2/25 - 21:08
@Author  :  Lee
@File    :  test_register
--------------------------------
"""
import pytest
import requests
from comms.excel_utils import ReadExcel
import allure
from comms.log_utils import logger
from comms.constants import DATA_FILE
from comms.db_utils import DBUtils


@allure.feature("注册模块")  # allure报告的模块分层
class TestRegister:
    @pytest.fixture(autouse=True)
    def connect_db(self):
        self.db = DBUtils()
        yield
        self.db.close()

    cases = ReadExcel.read_data_all(DATA_FILE, 'register')  # 读取excel的register的sheet页的所有测试用例对象返回列表

    @allure.severity("critical")  # 为allure报告修改case优先级
    @allure.description("京东小程序入口注册接口")  # 为allure报告添加case描述
    @pytest.mark.parametrize("case", cases)  # 把返回的列表中的成员赋值给case，每赋值一次执行一次case
    def test_register(self, case):  # 接受case测试用例对象参数
        allure.dynamic.title(case.case_title)  # 动态获取allure报告的case标题
        allure.attach(body=case.url, name='接口路径')  # allure报告显示接口路径
        allure.attach(body=case.case_data, name='接口参数')  # allure报告显示接口参数

        uname = eval(case.case_data)["username"]
        phone = eval(case.case_data)["phone"]
        # 正确流程
        if case.case_id == 1:
            self.db.cud("delete from tb_user where name = %s or phone = %s;", (uname, phone))

        response = requests.post(url=case.url, data=eval(case.case_data))  # 发起post请求，url和请求体是对像的2个实例属性
        res = response.json()  # 把响应体转换为jsio格式

        allure.attach(body=str(res), name='响应结果')  # allure报告显示响应结果

        try:
            assert eval(case.expect) == res  # 断言测试用例的预期结果和实际结果是否一致
            # 数据验证
            if case.case_id == 1:
                count = self.db.find_count('select * from tb_user where name = %s;', (uname,))
                assert count == 1
        except AssertionError as e:
            ReadExcel.write_data(DATA_FILE, 'register', case.case_id, 7,
                                 '失败')  # 如果断言失败把结果写入excel
            logger.error("测试编号{},测试用例标题{},执行失败！实际结果是:{}".format(case.case_id, case.case_title, res))
            logger.exception(e)
            raise e
        else:
            ReadExcel.write_data(DATA_FILE, 'register', case.case_id, 7,
                                 '成功')  # 如果实际结果和预期结果一致就把‘成功’写入excel
            logger.error("测试编号{},测试用例标题{},执行成功！".format(case.case_id, case.case_title))
