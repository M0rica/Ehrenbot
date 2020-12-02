import os
import json
import datetime

class Member:

    def __init__(self, member_id: int, name: str, save_dir: str):

        self.member_id = member_id
        self.name = name
        self.save_dir = save_dir
        self.balance = 0
        self.antispam_score = 0
        self.bans = 0
        self.warned = False
        self.transaction_hist = ''
        self.donated = False
        self.has_vote = False

        if self.has_account():
            self.load_account()

        else:
            self.create_account()

    def __str__(self):

        return f'<member_id={self.member_id}, balance={self.balance}, save_dir={self.save_dir}>'

    def __eq__(self, other):

        return self.member_id == other.member_id

    def has_account(self):

        if os.path.isfile(f'{self.save_dir}/accounts/{str(self.member_id)}.acc'):
            return True
        else:
            return False

    def create_account(self):

        self.transaction(1000, 'Startkapital')

    def load_account(self):

        with open(f'{self.save_dir}/accounts/{str(self.member_id)}.acc') as save:
            data = json.load(save)
        self.balance = data["balance"]
        self.bans = data["warns"]
        self.transaction_hist = data["transaction_hist"]
        self.donated = data["donated"]
        self.has_vote = data["has_vote"]

    def save(self):

        with open(f'{self.save_dir}/accounts/{str(self.member_id)}.acc', 'w') as save:
            data = {}
            data["balance"] = self.balance
            data["warns"] = self.bans
            data["transaction_hist"] = self.transaction_hist
            data["donated"] = self.donated
            data["has_vote"] = self.has_vote

            json.dump(data, save, indent=4)

    def transaction(self, amount: int, note: str):

        if self.balance + amount < 0:
            raise TransactionError(
                f'Amount to be deducted higher than account balance: tried removing {amount} from {self.balance}')
        self.balance += amount
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if amount > 0:
            symbol = '[+]'
        else:
            symbol = '[-]'
        self.transaction_hist += f'\n[{timestamp}] {symbol} **{str(amount).replace("-", "")}** {note}'
