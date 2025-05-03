from django.db import connection

class ProductCatalogClass:
    @staticmethod
    def addProductRecord(prod_category, prod_name, prod_desc, prod_price_inr, prod_price_usd, prod_image1, prod_image2, prod_image3):
        with connection.cursor() as cursor:
            cursor.execute("CALL add_product(%s, %s, %s, %s, %s, %s, %s, %s, @msg);",
                           [prod_category, prod_name, prod_desc, prod_price_inr, prod_price_usd, prod_image1, prod_image2, prod_image3])
            cursor.execute("SELECT @msg;")
            resultMsg = cursor.fetchone()[0]
        return resultMsg
    

    @staticmethod
    def updateProductRecord(prod_id, prod_category, prod_name, prod_desc, prod_price_inr, prod_price_usd, prod_image1, prod_image2, prod_image3):
        with connection.cursor() as cursor:
            cursor.execute("""
                CALL update_product(%s, %s, %s, %s, %s, %s, %s, %s, %s, @msg);
            """, [prod_id, prod_category, prod_name, prod_desc, prod_price_inr, prod_price_usd, prod_image1, prod_image2, prod_image3])
            
            cursor.execute("SELECT @msg;")
            resultMsg = cursor.fetchone()[0]
        
        return resultMsg