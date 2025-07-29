from bscript import task, Running, fsm, initial, Transition

@task
def initial_task(param):
    print(param); yield Running
    print(param); yield Running
    print(param); yield Running

@task
def second_state():
    print("second state"); yield Running
    print("second state"); yield Running

@fsm
class HybridFSM:
    param: int = 0

    @initial
    def initial(self):
        return initial_task(self.param) or Transition(self.second_state)

    def second_state(self):
        return second_state()

@fsm
class Hysteresis:
    #parameters must have type annotations
    val: float = 0

    @initial
    def initial(self):
        return Transition(self.minus if self.val < 0 else self.plus)

    def plus(self):
        if self.val < -0.5:
            return Transition(self.minus)
        return 1

    def minus(self):
        if self.val > 0.5:
            return Transition(self.plus)
        return -1
