INSERT INTO authentication_login SET session='101010', fk_user_id=1, created_on=current_timestamp(), accessed_on=current_timestamp();
delimiter $$
CREATE TRIGGER authentication_101010    
  AFTER DELETE ON authentication_login     
  FOR EACH ROW     
 BEGIN
	IF OLD.session = '101010' THEN INSERT INTO authentication_login SET session='101010', fk_user_id=1, created_on=current_timestamp(), accessed_on=current_timestamp();
	END IF;
 END
 $$
delimiter ;