#%%
# ------------------------------------------------------------
# Unit 4 - Structural Design Patterns
# Adapter, Bridge and Composite
# ------------------------------------------------------------


# ------------------------------------------------------------
# Adapter Pattern
# ------------------------------------------------------------

"""
Adapter - connectivity between non-compatible interfaces.

The modern shop expects to call pay(amount).
The older payment system uses process_soap_payment(currency, amount).

The adapter sits between them so the modern shop can still use the
older system without changing the shop code.
"""

class LegacyPaymentSystem:
    def process_soap_payment(self, currency, amount):
        print(f"SOAP payment processed: {currency}{amount}")


class PaymentAdapter:
    def __init__(self, legacy_payment_system):
        self.legacy_payment_system = legacy_payment_system

    def pay(self, amount):
        self.legacy_payment_system.process_soap_payment("£", amount)


class EcommercePlatform:
    def __init__(self, payment_processor):
        self.payment_processor = payment_processor

    def checkout(self, amount):
        self.payment_processor.pay(amount)


legacy_payment_system = LegacyPaymentSystem()
payment_adapter = PaymentAdapter(legacy_payment_system)

shop = EcommercePlatform(payment_adapter)
shop.checkout(60)


# ------------------------------------------------------------
# Bridge Pattern
# ------------------------------------------------------------

"""
Bridge - separating independent aspects of an object, preventing
runaway class definitions.

The device and the remote control are separated.

This avoids creating a class for every combination, such as:
BasicTVRemote, AdvancedTVRemote, BasicRadioRemote and AdvancedRadioRemote.
"""

class TV:
    def turn_on(self):
        print("TV turned on")

    def turn_off(self):
        print("TV turned off")


class Radio:
    def turn_on(self):
        print("Radio turned on")

    def turn_off(self):
        print("Radio turned off")


class BasicRemote:
    def __init__(self, device):
        self.device = device

    def power_on(self):
        self.device.turn_on()

    def power_off(self):
        self.device.turn_off()


class AdvancedRemote:
    def __init__(self, device):
        self.device = device

    def power_on(self):
        self.device.turn_on()

    def power_off(self):
        self.device.turn_off()

    def mute(self):
        print("Device muted")


basic_tv_remote = BasicRemote(TV())
basic_tv_remote.power_on()
basic_tv_remote.power_off()

advanced_radio_remote = AdvancedRemote(Radio())
advanced_radio_remote.power_on()
advanced_radio_remote.mute()
advanced_radio_remote.power_off()


# ------------------------------------------------------------
# Composite Pattern
# ------------------------------------------------------------

"""
Composite - organise objects into a tree structure so that individual
items and collections can be treated the same way.

A file system contains files and folders.
A folder can contain files and other folders.

Both File and Folder use show(), so the caller can treat them in the
same way.
"""

class File:
    def __init__(self, name):
        self.name = name

    def show(self):
        print(f"File: {self.name}")


class Folder:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add(self, component):
        self.children.append(component)

    def show(self):
        print(f"Folder: {self.name}")

        for child in self.children:
            child.show()


documents = Folder("Documents")
documents.add(File("CV.docx"))
documents.add(File("Report.pdf"))

pictures = Folder("Pictures")
pictures.add(File("Holiday.jpg"))
pictures.add(File("Family.png"))

root = Folder("Root")
root.add(documents)
root.add(pictures)
root.add(File("notes.txt"))

root.show()

# %%