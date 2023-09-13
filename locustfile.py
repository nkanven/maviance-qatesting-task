import os
from locust import HttpUser, task, between
from dotenv import load_dotenv

load_dotenv()


class Smobilpay(HttpUser):
    wait_time = between(1, 5)

    @task
    def home(self):
        self.client.get("")

    def on_start(self):
        self.client.post(os.getenv("user"),
                         json={"email": os.getenv("user"), "password": os.getenv("password")})
