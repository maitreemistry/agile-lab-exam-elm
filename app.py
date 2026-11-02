class LeaveManager:
    def __init__(self, leave_balances: dict[str, int]):
        self.leave_balances = leave_balances.copy()

    def leaves_left(self, employee: str) -> int:
        return self.leave_balances[employee]

    def request_leave(self, employee: str, days: int) -> bool:
        if days <= 0:
            raise ValueError("Leave days must be positive")

        if days > self.leaves_left(employee):
            return False

        self.leave_balances[employee] -= days
        return True


if __name__ == "__main__":
    manager = LeaveManager({"Alex": 20})
    approved = manager.request_leave("Alex", 3)
    print(f"Leave request {'approved' if approved else 'denied'}")
    print(f"Leaves left: {manager.leaves_left('Alex')}")