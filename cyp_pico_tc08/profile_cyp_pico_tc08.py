import cProfile
import cyp_pico_tc08

with cProfile.Profile() as initialize:
    controller = cyp_pico_tc08.PicoController()

channel = "Temp 1-1"
with cProfile.Profile() as access:
    value = controller.read(channel)
print(f"Read temp: {value}")

print("Initialization Profile:")
initialize.print_stats(sort="cumtime")
print("Reading Profile:")
access.print_stats(sort="cumtime")
access.print_callees()
