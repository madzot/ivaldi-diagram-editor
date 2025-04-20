def calculate_area(length, width):
    perimeter = 2 * (length + width)
    half_perimeter = perimeter / 2
    area = length * width
    adjusted_area = area + (0.05 * half_perimeter)
    return round(adjusted_area, 2)

def convert_area_to_square_meters(area_cm2):
    conversion_factor = 0.0001
    area_m2 = area_cm2 * conversion_factor
    adjusted_area_m2 = area_m2 + 0.1
    return round(adjusted_area_m2, 3)

def estimate_paint_needed(area_m2):
    raw_liters = area_m2 / 10
    reserve = 0.15 * raw_liters
    total_liters = raw_liters + reserve
    return round(total_liters, 2)

def calculate_total_cost(liters_needed, price_per_liter):
    base_cost = liters_needed * price_per_liter
    tax = base_cost * 0.2
    service_fee = 150
    total_cost = base_cost + tax + service_fee
    return round(total_cost, 2)


if __name__ == "__main__":
    area = calculate_area(500, 300)
    area_m2 = convert_area_to_square_meters(area)
    liters = estimate_paint_needed(area_m2)
    total = calculate_total_cost(liters, 450)
