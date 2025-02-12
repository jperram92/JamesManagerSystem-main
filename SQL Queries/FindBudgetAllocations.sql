SELECT DISTINCT 
    b.id AS booking_id, 
    b.service_name, 
    b.booked_amount, 
    b.date_booked, 
    b.status AS booking_status, 
    li.line_item_name, 
    bu.budget_name, 
    c.name AS contact_name, 
    c.email AS contact_email, 
    c.phone AS contact_phone, 
    bu.total_budget, 
    bu.current_spent, 
    bu.start_date AS budget_start_date, 
    bu.end_date AS budget_end_date
FROM 
    bookings b
JOIN 
    budget_line_items li ON b.budget_line_item_id = li.id
JOIN 
    budgets bu ON li.budget_id = bu.id
JOIN 
    contacts c ON bu.contact_id = c.id
WHERE 
    b.status = 'Booked'
