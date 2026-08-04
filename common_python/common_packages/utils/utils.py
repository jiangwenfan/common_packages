import logging
import smtplib
from email.mime.text import MIMEText


def calculate_relative_value(input_data: list, db_data: list) -> float:
    """计算input_data中db_data所占的比例"""
    # 去重
    input_data_unique: set = set(input_data)
    db_data_unique: set = set(db_data)
    # 获取交集.
    # 获取input_data中db_data的数据
    intersection: set = input_data_unique.intersection(db_data_unique)

    # 获取input_data中db_data所占的比例
    result: float = len(intersection) / len(input_data_unique)
    return result


class SendEmail:
    def __init__(self, config: dict) -> None:
        if not set(config).issubset({"host", "port", "user", "passwd"}):
            raise ValueError("config must contain host, user, pass, sender")
        self.host = config["host"]
        self.user = config["user"]
        self.port = config["port"]
        self.passwd = config["passwd"]

    def send_txt_message(
        self, receivers: list, subject: str, content: str
    ) -> tuple[bool, str]:
        """发送文本邮件, 返回发送状态和错误信息"""
        message = MIMEText(content, "plain", "utf-8")
        message["From"] = f"{self.user}"
        message["To"] = ",".join(receivers)
        message["Subject"] = subject

        try:
            smtpObj = smtplib.SMTP_SSL(self.host, self.port)
            smtpObj.login(self.user, self.passwd)
            smtpObj.sendmail(self.user, receivers, message.as_string())
            logging.info(f"mail has been send successfully. {receivers}")
            return True, "success"
        except smtplib.SMTPException as e:
            logging.error(e)
            return False, str(e)
