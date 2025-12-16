USE takapi;

-- ADD EXPENSE ---------------------------------------------
DROP PROCEDURE IF EXISTS sp_add_expense;
DELIMITER // 
CREATE PROCEDURE sp_add_expense(
	IN p_amount DECIMAL(12, 2),
    IN p_date DATE,
    IN p_user_id INT,
    IN p_category_id INT,
    IN p_description VARCHAR(255)
)
BEGIN
	INSERT INTO expense_expense(amount, date, user_id, category_id, description)
    VALUES (p_amount, p_date, p_user_id, p_category_id, p_description);
    
    SELECT LAST_INSERT_ID() AS new_expense_id;
END//
DELIMITER ;

-- GET USER EXPENSE ---------------------------------------------
DROP PROCEDURE IF EXISTS sp_get_user_expenses;
DELIMITER // 
CREATE PROCEDURE sp_get_user_expenses(
	IN p_user_id INT
)
BEGIN
	SELECT e.expense_id, e.amount, e.date, e.description, c.name AS category_name, c.category_id
    FROM expense_expense e
    JOIN expense_expensecategory c ON e.category_id = c.category_id
    WHERE e.user_id = p_user_id
    ORDER BY e.date DESC;
END //
DELIMITER ;

-- ORDER EXPENSE BY CATEGORY---------------------------------------------
DROP PROCEDURE IF EXISTS sp_expenses_by_category;
DELIMITER //
CREATE PROCEDURE sp_expenses_by_category(
	IN p_user_id INT
)
BEGIN
	SELECT c.category_id, 
        c.name AS category_name,
		COUNT(e.expense_id) AS expense_count,
		COALESCE(SUM(e.amount), 0) AS total_amount
    FROM expense_expensecategory c
    LEFT JOIN expense_expense e ON c.category_id = e.category_id
		AND e.user_id = p_user_id
	WHERE c.user_id = p_user_id
    GROUP BY c.category_id, c.name
    ORDER BY total_amount DESC;
END //
DELIMITER ;

-- UPDATE EXPENSE ---------------------------------------------
DROP PROCEDURE IF EXISTS sp_update_expense;
DELIMITER //
CREATE PROCEDURE sp_update_expense(
    IN p_expense_id INT,
    IN p_amount DECIMAL(12, 2),
    IN p_date DATE,
    IN p_category_id INT,
    IN p_description VARCHAR(255)
)
BEGIN
    UPDATE expense_expense
    SET 
        amount = p_amount,
        date = p_date,
        category_id = p_category_id,
        description = p_description
    WHERE expense_id = p_expense_id;
    
    SELECT ROW_COUNT() AS rows_updated;
END //
DELIMITER ;

-- DELETE EXPENSE ---------------------------------------------
DROP PROCEDURE IF EXISTS sp_delete_expense;
DELIMITER //
CREATE PROCEDURE sp_delete_expense(
    IN p_expense_id INT,
    IN p_user_id INT
)
BEGIN
    DELETE FROM expense_expense
    WHERE expense_id = p_expense_id AND user_id = p_user_id;
    
    SELECT ROW_COUNT() AS rows_deleted;
END //
DELIMITER ;

-- MONTHLY SUMMAY ---------------------------------------------
DROP PROCEDURE IF EXISTS sp_monthly_summary;
DELIMITER //
CREATE PROCEDURE sp_monthly_summary(
    IN p_user_id INT,
    IN p_year INT,
    IN p_month INT
)
BEGIN
    SELECT 
        COUNT(*) AS total_transactions,
        COALESCE(SUM(amount), 0) AS total_spent,
        COALESCE(AVG(amount), 0) AS average_expense,
        COALESCE(MAX(amount), 0) AS largest_expense,
        COALESCE(MIN(amount), 0) AS smallest_expense
    FROM expense_expense
    WHERE user_id = p_user_id
      AND YEAR(date) = p_year
      AND MONTH(date) = p_month;
END //
DELIMITER ;

-- ADD CATEGORY ---------------------------------------------
DROP PROCEDURE IF EXISTS sp_add_category;
DELIMITER //
CREATE PROCEDURE sp_add_category(
    IN p_name VARCHAR(100),
	IN p_user_id INT
)
BEGIN
    IF EXISTS (SELECT 1 FROM expense_expensecategory WHERE name = p_name AND user_id = p_user_id) THEN
        SELECT -1 AS new_category_id;
    ELSE
        INSERT INTO expense_expensecategory(name, user_id)
        VALUES (p_name, p_user_id);
    
        SELECT LAST_INSERT_ID() AS new_category_id;
    END IF;
END//
DELIMITER ;

-- UPDATE CATEGORY ---------------------------------------------
DROP PROCEDURE IF EXISTS sp_update_category;
DELIMITER //
CREATE PROCEDURE sp_update_category(
    IN p_category_id INT,
    IN p_name VARCHAR(100),
    IN p_user_id INT
)
BEGIN
    UPDATE expense_expensecategory
    SET name = p_name
    WHERE category_id = p_category_id AND user_id = p_user_id;
    
    SELECT ROW_COUNT() AS rows_updated;
END //
DELIMITER ;

-- DELETE CATEGORY ---------------------------------------------
DROP PROCEDURE IF EXISTS sp_delete_category;
DELIMITER //
CREATE PROCEDURE sp_delete_category(
	IN p_category_id INT,
    IN p_user_id INT
)
BEGIN
    -- Check if ANY expense exists for this category
    IF EXISTS (SELECT 1 FROM expense_expense WHERE category_id = p_category_id) THEN
        -- Do NOT delete.
        SELECT -1 AS rows_deleted;
    ELSE
        -- Safe to delete
        DELETE FROM expense_expensecategory
        WHERE category_id = p_category_id AND user_id = p_user_id;
        
        SELECT ROW_COUNT() AS rows_deleted;
    END IF;
END //
DELIMITER ;