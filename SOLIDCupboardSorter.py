#%%
""" 
Version 1, intentionally bad but real world enough to explain in laymans terms
Sorting a cupboard - the class contains everything, bagging and throwing all items
"""
class SortCupboard:

    def __init__(self):
        self.items = [
            "old cables",
            "spare clothes",
            "expired batteries",
            "random manuals"
        ]

    def sort_items(self):

        for item in self.items:
            print(f"Bagging {item}")
            print(f"Throwing {item} in trash")
# %%
"""
Applying a SOLID approach, the same results but 
with TrashAction.handle separated for clarity (modularity) and 
introduced to allow extensibility

CupboardItem defines the items, 
TrashAction defines the outcome, 
CupboardSorter applies the actions to the items
"""
class CupboardItem:
    def __init__(self, name):
        self.name = name

items = [
    CupboardItem("old cables"),
    CupboardItem("spare clothes"),
    CupboardItem("expired batteries"),
    CupboardItem("random manuals")
]

class TrashAction:
    def handle(self, item):
        print(f"Bagging {item.name}")
        print(f"Throwing {item.name} in trash")


class CupboardSorter:
    def sort(self, items):

        for item in items:
            TrashAction().handle(item)

sorter = CupboardSorter()
sorter.sort(items)
#%%
"""
implementing a SOLID approach to a further degree, the result now depends on a decision tree. 
Each result leads to a class which contains 'handle'
This also allows for additional branches and actions, e.g.
(value = unknown, action 'ask the wife' : recyclable = hazardous, action 'arrange collection')
A decision tree was used to avoid forcing properties on CupboardItem which could be unneccessary e.g.
valued items don't need a recyclable property as they're not being thrown away
"""
class CupboardItem:
    def __init__(self, name):
        self.name = name

items = [
    CupboardItem("old cables"),
    CupboardItem("spare clothes"),
    CupboardItem("expired batteries"),
    CupboardItem("random manuals")
]

class KeepAction:
    def handle(self, item):
        print(f"Returning {item.name} to cupboard")

class DonateAction:
    def handle(self, item):
        print(f"Donating {item.name}")

class BlueBinAction:
    def handle(self, item):
        print(f"Putting {item.name} in blue bin")

class BlackBinAction:
    def handle(self, item):
        print(f"Putting {item.name} in black bin")

class CupboardSorter:
    def sort(self, items):

        for item in items:

            has_value = input(f"Does {item.name} have value? (yes/no): ")

            if has_value.lower() == "yes":

                keep = input(f"Keep {item.name}? (yes/no): ")

                if keep.lower() == "yes":
                    KeepAction().handle(item)
                else:
                    DonateAction().handle(item)

            else:

                recyclable = input(f"Is {item.name} recyclable? (yes/no): ")

                if recyclable.lower() == "yes":
                    BlueBinAction().handle(item)
                else:
                    BlackBinAction().handle(item)

sorter = CupboardSorter()
sorter.sort(items)
