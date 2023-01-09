from aiogram.fsm.state import State, StatesGroup


# class for watch state of add/remove subscribes
class FSMUpdateSubs(StatesGroup):
    started = State()
    add = State()
    remove = State()
