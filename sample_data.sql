-- Sample data for the restaurant system.
-- Use this file as reference, or run the Python seed script for proper password hashing.

INSERT INTO food_categories (name, description) VALUES
  ('Starters', 'Light appetizers to begin the meal'),
  ('Main Course', 'Hearty and flavorful main dishes'),
  ('Desserts', 'Sweet treats to finish your dining experience'),
  ('Beverages', 'Cold and hot beverages');

INSERT INTO food_items (category_id, name, description, price, image_filename, is_available) VALUES
  (1, 'Bruschetta', 'Toasted bread topped with tomatoes and basil.', 8.50, 'img/ragul.png.jpg', TRUE),
  (1, 'Garlic Fries', 'Crispy fries tossed with garlic and herbs.', 6.50, 'img/ragul.png.jpg', TRUE),
  (2, 'Grilled Salmon', 'Pan-seared salmon with seasonal vegetables.', 18.99, 'img/ragul.png.jpg', TRUE),
  (2, 'Chicken Curry', 'Spicy chicken curry served with rice.', 16.75, 'img/ragul.png.jpg', TRUE),
  (3, 'Chocolate Lava Cake', 'Warm chocolate cake with a molten center.', 7.50, 'img/ragul.png.jpg', TRUE),
  (4, 'Classic Lemonade', 'Refreshing freshly squeezed lemonade.', 4.50, 'img/ragul.png.jpg', TRUE);

INSERT INTO tables (table_number, capacity, location, is_available) VALUES
  ('A1', 2, 'Window', TRUE),
  ('A2', 4, 'Window', TRUE),
  ('B1', 4, 'Center', TRUE),
  ('B2', 6, 'Center', TRUE),
  ('C1', 8, 'Private', TRUE);
