-- trigger_review_log.sql - demonstrates an AFTER INSERT trigger
-- This is a separate script (not auto-run by init_db) meant to be executed manually.
-- It creates a log table that automatically records every new rating.

USE sobkaj;

-- log table to keep a record of every review that gets submitted
CREATE TABLE IF NOT EXISTS review_log (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    rating_id   INT NOT NULL,
    booking_id  INT NOT NULL,
    worker_id   INT NOT NULL,
    stars       INT NOT NULL,
    logged_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- this trigger fires automatically after a new row is inserted into ratings
-- it copies the key fields into review_log so we have an audit trail
DELIMITER $$

CREATE TRIGGER trg_after_review_insert
AFTER INSERT ON ratings
FOR EACH ROW
BEGIN
    INSERT INTO review_log (rating_id, booking_id, worker_id, stars)
    VALUES (NEW.rating_id, NEW.booking_id, NEW.worker_id, NEW.stars);
END$$

DELIMITER ;
