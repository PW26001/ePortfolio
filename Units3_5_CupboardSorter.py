#%%

"""
This develops the Cupboard Sorter example by applying
design patterns where appropriate

Patterns I was able to apply:
- Factory Method
- Decorator
- Strategy
- Chain of Responsibility
"""


# ------------------------------------------------------------
# Shared Item
# ------------------------------------------------------------

class CupboardItem:
    def __init__(self, name, has_value=False, keep=False, recyclable=False, hazardous=False):
        self.name = name
        self.has_value = has_value
        self.keep = keep
        self.recyclable = recyclable
        self.hazardous = hazardous

class KeepAction:
    def handle(self, item):
        print(f"Returning {item.name} to the cupboard")

class DonateAction:
    def handle(self, item):
        print(f"Donating {item.name}")

class BlueBinAction:
    def handle(self, item):
        print(f"Putting {item.name} in the blue bin")

class BlackBinAction:
    def handle(self, item):
        print(f"Putting {item.name} in the black bin")

class HazardousWasteAction:
    def handle(self, item):
        print(f"Arranging safe collection for {item.name}")


"""
Decorator - adding behaviour
"""

class LoggingDecorator:
    def __init__(self, action):
        self.action = action

    def handle(self, item):
        print(f"LOG: Starting action for {item.name}")
        self.action.handle(item)
        print(f"LOG: Finished action for {item.name}")


class ApprovalDecorator:
    def __init__(self, action):
        self.action = action

    def handle(self, item):
        print(f"Approval checked for {item.name}")
        self.action.handle(item)


# ------------------------------------------------------------
# Factory Method Pattern
# ------------------------------------------------------------

"""
Factory Method - CupboardSorter asks the factory for the action.
"""

class CupboardActionFactory:
    def create_action(self, item):
        if item.hazardous:
            return HazardousWasteAction()

        if item.has_value and item.keep:
            return KeepAction()

        if item.has_value and not item.keep:
            return LoggingDecorator(DonateAction())

        if item.recyclable:
            return BlueBinAction()

        return BlackBinAction()


# ------------------------------------------------------------
# Chain of Responsibility Pattern
# ------------------------------------------------------------

"""
Chain of Responsibility 
"""

class Handler:
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    def handle(self, item):
        if self.next_handler:
            return self.next_handler.handle(item)

        print(f"No handler found for {item.name}")


class HazardousHandler(Handler):
    def handle(self, item):
        if item.hazardous:
            HazardousWasteAction().handle(item)
        else:
            super().handle(item)


class KeepHandler(Handler):
    def handle(self, item):
        if item.has_value and item.keep:
            KeepAction().handle(item)
        else:
            super().handle(item)


class DonateHandler(Handler):
    def handle(self, item):
        if item.has_value and not item.keep:
            LoggingDecorator(DonateAction()).handle(item)
        else:
            super().handle(item)


class RecycleHandler(Handler):
    def handle(self, item):
        if item.recyclable:
            BlueBinAction().handle(item)
        else:
            super().handle(item)


class GeneralWasteHandler(Handler):
    def handle(self, item):
        BlackBinAction().handle(item)


# ------------------------------------------------------------
# Cupboard Sorter
# ------------------------------------------------------------

class CupboardSorter:
    def __init__(self, action_factory=None, handler_chain=None):
        self.action_factory = action_factory
        self.handler_chain = handler_chain

    def sort_with_factory(self, items):
        print("Sorting with Factory Method")
        print("---------------------------")

        for item in items:
            action = self.action_factory.create_action(item)
            action.handle(item)

    def sort_with_chain(self, items):
        print("Sorting with Chain of Responsibility")
        print("------------------------------------")

        for item in items:
            self.handler_chain.handle(item)


# ------------------------------------------------------------
# Demos
# ------------------------------------------------------------

items = [
    CupboardItem("spare clothes", has_value=True, keep=True),
    CupboardItem("old coat", has_value=True, keep=False),
    CupboardItem("expired batteries", hazardous=True),
    CupboardItem("cardboard box", recyclable=True),
    CupboardItem("random manuals")
]


# Factory Method demo
factory = CupboardActionFactory()
factory_sorter = CupboardSorter(action_factory=factory)
factory_sorter.sort_with_factory(items)

print()


# Decorator demo
decorated_action = ApprovalDecorator(
    LoggingDecorator(
        DonateAction()
    )
)

decorated_action.handle(CupboardItem("old toys", has_value=True, keep=False))

print()


# Chain of Responsibility demo
chain = HazardousHandler(
    KeepHandler(
        DonateHandler(
            RecycleHandler(
                GeneralWasteHandler()
            )
        )
    )
)

chain_sorter = CupboardSorter(handler_chain=chain)
chain_sorter.sort_with_chain(items)

# %%