import threading
class MultiLevelParking:
    def __init__(self, levels, slots_per_level):
        if len(slots_per_level) != levels:
            raise ValueError("The length of slots_per_level should match the number of levels")

        self.levels = levels
        self.slots_per_level = slots_per_level
        self.parking_area = {level: [None] * slots for level, slots in enumerate(slots_per_level)}
        self.vehicle_records = {}
        self.valid_vehicle_types = {"Car", "Bike", "Truck"}  # Using a set for faster lookups

    # Thread safety
        self.lock = threading.Lock()


    def allocate_parking(self, reg_number, vehicle_kind):
        with self.lock:  # Ensure thread-safety by locking this section
            # Check if the vehicle type is valid
            if vehicle_kind not in self.valid_vehicle_types:
                return "Invalid vehicle category"
            
            # Check if the vehicle is already parked
            if reg_number in self.vehicle_records:
                return "Vehicle already parked"

            # Try to park the vehicle
            # we are trying to find the just next free slot on current level 
            # and if we do not find any empty slot on the current level then
            # we search for the empty slot in the next level by iterating through each level 
            for lvl in range(self.levels):
                for slot in range(self.slots_per_level[lvl]):
                    if self.is_slot_free(lvl, slot, vehicle_kind):
                        if vehicle_kind == "Truck":
                            # Park truck in two consecutive spots
                            self.parking_area[lvl][slot] = reg_number
                            self.parking_area[lvl][slot + 1] = reg_number
                            self.vehicle_records[reg_number] = (lvl, slot, slot + 1)
                        else:
                            self.parking_area[lvl][slot] = reg_number
                            self.vehicle_records[reg_number] = (lvl, slot)
                        return f"Vehicle {reg_number} parked at level {lvl}, slot {slot}"

            # If no spot found, try to find a spot on the next floor with available space
            for lvl in range(self.levels):
                if self.is_any_floor_available(lvl):
                    for spot in range(self.slots_per_level[lvl]):
                        if self.is_slot_free(lvl, spot, vehicle_kind):
                            if vehicle_kind == "Truck":
                                # Park truck in two consecutive spots
                                self.parking_area[lvl][spot] = reg_number
                                self.parking_area[lvl][spot + 1] = reg_number
                                self.vehicle_records[reg_number] = (lvl, spot, spot + 1)
                            else:
                                self.parking_area[lvl][spot] = reg_number
                                self.vehicle_records[reg_number] = (lvl, spot)
                            return f"Vehicle {reg_number} parked at level {lvl}, slot {spot}"

            return "Parking area is full"

    def release_parking(self, reg_number):
        with self.lock:  # Ensure thread-safety by locking this section
            # if vehicle is not already parked
            if reg_number not in self.vehicle_records:
                return f"Vehicle {reg_number} is not parked in the area."
            
            # Retrieve the vehicle's location 
            location = self.vehicle_records.pop(reg_number)
            level, slot = location[0], location[1]
            
            if len(location) == 2:  # For Car or Bike
                self.parking_area[level][slot] = None
            else:  # For Truck (which occupies two spots)
                second_slot = location[2]  # Ensure correct indexing
                self.parking_area[level][slot] = None
                self.parking_area[level][second_slot] = None  # Free second slot
            
            return f"Vehicle {reg_number} has been unparked"

    def is_slot_free(self, level, slot, vehicle_kind):
        if self.parking_area[level][slot] is not None:
            return False
        
        if vehicle_kind == "Truck":
            # Truck needs 2 consecutive spots
            if slot + 1 < self.slots_per_level[level] and self.parking_area[level][slot + 1] is None:
                return True
        elif vehicle_kind in ["Car", "Bike"]:
            return True
        
        return False

    def is_any_floor_available(self, level):
        # Check if there is any available spot on the given floor
        for slot in range(self.slots_per_level[level]):
            if self.is_slot_free(level, slot, "Car") or self.is_slot_free(level, slot, "Bike") or self.is_slot_free(level, slot, "Truck"):
                return True
        return False

    def count_vacant_slots(self):
     # Returns a dictionary with the count of vacant slots for each level.
        with self.lock:  # Ensure thread-safety
            free_slots = {
                level: self.parking_area[level].count(None) for level in range(self.levels)
            }
            return free_slots


    def is_full(self):
    # Check if the parking area is completely occupied.
        with self.lock:  # Ensure thread-safety
            for level in self.parking_area.values():
                if any(slot is None for slot in level):  # If any slot is empty, parking is not full
                    return False
            return True  # All slots are occupied


    def locate_vehicle(self, reg_number):
        with self.lock:  # Ensure thread-safety by locking this section
            if reg_number in self.vehicle_records:
                return self.vehicle_records[reg_number]
            return "Vehicle not found"


# Main function to run the System
def run_parking_system():
    # Get number of levels and slots per level from the user
    levels = int(input("Enter number of levels in the parking area: "))
    slots_per_level = []
    
    for i in range(levels):
        slots = int(input(f"Enter the number of slots for level {i + 1}: "))
        slots_per_level.append(slots)

    # Create ParkingSystem object with user input
    parking_system = MultiLevelParking(levels, slots_per_level)
    while True:
        print("\nParking Management System")
        print("1. Check Available Slots")
        print("2. Park a Vehicle")
        print("3. Find Vehicle Location")
        print("4. Unpark a Vehicle ")
        print("5. Exit")

        user_choice = input("Choose an option (1-5): ")

        if user_choice == "1":
            print(parking_system.count_vacant_slots())
            

        elif user_choice == "2":
            reg_number = input("Enter vehicle registration number: ")
            vehicle_kind = input("Enter vehicle type (Car/Bike/Truck): ")
            print(parking_system.allocate_parking(reg_number, vehicle_kind))

        elif user_choice == "3":
            reg_number = input("Enter Vehicle registration number to locate: ")
            print(parking_system.locate_vehicle(reg_number))

        elif user_choice == "4":
            reg_number = input("Enter vehicle registration number to unpark: ")
            print(parking_system.release_parking(reg_number))

        elif user_choice == "5":
            print("Shutting down the system...")
            break

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    run_parking_system()
