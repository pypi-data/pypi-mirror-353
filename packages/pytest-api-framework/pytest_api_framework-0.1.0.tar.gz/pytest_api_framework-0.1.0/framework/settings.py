import os
from dotenv import load_dotenv

load_dotenv()
# 项目跟目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 生成allure报告程序的路径
ALLURE_DIR = os.getenv("ALLURE_DIR")
# allure统计执行结果目录
ALLURE_RESULTS_DIR = os.path.join(ROOT_DIR, "allure_results")
# allure报告目录
ALLURE_REPORT_DIR = os.path.join(ROOT_DIR, "allure_report")
# allure报告统计执行环境的存放路径
ALLURE_ENV_PROPERTIES = os.path.join(ALLURE_RESULTS_DIR, "environment.properties")
# 存放case的目录
CASES_DIR = os.path.join(ROOT_DIR, "test_case")
# 存放测试数据的目录
DATA_DIR = os.path.join(ROOT_DIR, "test_data")
# 存放配置的目录
CONFIG_DIR = os.path.join(ROOT_DIR, "config")