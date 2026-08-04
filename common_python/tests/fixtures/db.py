import subprocess
import time

import pymysql
import pytest

from common_packages.db_utils.mysql import MysqlOperator
from tests.fixtures.utils import parse_container_status


@pytest.fixture(scope="class")
def start_stop_mysql():
    """用于在`整个mysql测试类`中启动和关闭mysql服务"""
    print("启动临时mysql服务, test_services/compose-mysql.yml")
    subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            "test_services/compose-mysql.yml",
            "up",
            "-d",
        ],
        check=True,
    )
    # 等待mysql服务启动，如果超过120秒还没有成功启动，则则退出
    num = 0
    while num < 120:
        health_status = parse_container_status("temp-mysql")
        if health_status == "healthy":
            print("mysql服务启动成功....")
            break
        num += 1
        time.sleep(1)
    else:
        raise TimeoutError("mysql服务启动超时")

    yield "mysql"

    print("关闭临时mysql服务, test_services/compose-mysql.yml")
    subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            "test_services/compose-mysql.yml",
            "down",
        ],
        check=True,
    )


@pytest.fixture(scope="class")
def mysql_op(global_config):
    """用于在`整个mysql测试类`中初始化mysql操作对象"""
    mysql_config: dict = global_config["db"]["mysql"]
    mysql_op = MysqlOperator(**mysql_config)
    return mysql_op


@pytest.fixture(scope="function")
def reset_default_data(global_config):
    """用于在`每个测试方法`中重置数据"""
    connection = pymysql.connect(**global_config["db"]["mysql"])
    try:
        # 1. 清空 orders 表和 customers 表
        with connection.cursor() as cursor:
            sql = "delete from orders;"
            cursor.execute(sql)

            sql = "delete from customers;"
            cursor.execute(sql)

            connection.commit()

        # 2. 插入数据到 customers 表和 orders 表
        with connection.cursor() as cursor:
            sql = """INSERT INTO customers (customer_id,customer_name, email) VALUES\
(1,'Alice Smith', 'alice@example.com'),(2,'Bob Johnson', 'bob@example.com'),\
(3,'Charlie Lee', 'charlie@example.com');"""
            cursor.execute(sql)

            sql = """INSERT INTO orders (order_date, amount, customer_id) \
VALUES('2024-08-01', 250.75, 1),('2024-08-02', 100.00, 2),('2024-08-03', 300.50, 3)"""
            cursor.execute(sql)

            connection.commit()

        # 3. 查询表中的数据以确认插入成功
        with connection.cursor() as cursor:
            # 执行查询记录条数的 SQL 语句
            sql = "SELECT COUNT(*) FROM customers"
            cursor.execute(sql)
            result = cursor.fetchone()  # 这里返回的是一个元组 (count,)
            count = result[0]
            assert count == 3, f"customers 表中的数据不正确,期望是3条,实际{count}条"

            # 执行查询记录条数的 SQL 语句
            sql = "SELECT COUNT(*) FROM orders"
            cursor.execute(sql)
            result = cursor.fetchone()
            count = result[0]
            assert count == 3, f"orders 表中的数据不正确,期望是3条,实际{count}条"

    finally:
        # 关闭连接
        connection.close()
    yield "reset data"
