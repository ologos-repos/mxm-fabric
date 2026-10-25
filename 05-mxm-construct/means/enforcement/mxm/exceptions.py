class MxmError(Exception):
    pass


class IllegalTransition(MxmError):
    def __init__(self, current, target):
        super().__init__(f"illegal transition {current} -> {target}")
        self.current = current
        self.target = target


class NotOperator(MxmError):
    pass


class BlockedByAdvisor(MxmError):
    pass


class NeedAcceptance(MxmError):
    pass


class ConstitutionMismatch(MxmError):
    pass
