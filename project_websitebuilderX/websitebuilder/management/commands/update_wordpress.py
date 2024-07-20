from django.core.management.base import BaseCommand
import mysql.connector
from mysql.connector import Error
import os

class Command(BaseCommand):
    help = 'Update WordPress site information'

    def add_arguments(self, parser):
        parser.add_argument('--db-name', type=str, help='WordPress database name')
        parser.add_argument('--db-user', type=str, help='WordPress database user')
        parser.add_argument('--db-password', type=str, help='WordPress database password')
        parser.add_argument('--db-host', type=str, help='WordPress database host')
        parser.add_argument('--title', type=str, help='New site title')
        parser.add_argument('--description', type=str, help='New site description')
        # parser.add_argument('--logo-url', type=str, help='New logo URL')
        # parser.add_argument('--new-text', type=str, help='New text to set')
        parser.add_argument('--admin-email', type=str, help='New admin email')
        

    def handle(self, *args, **kwargs):
        db_name = kwargs.get('db_name')
        db_user = kwargs.get('db_user')
        db_password = kwargs.get('db_password')
        db_host = kwargs.get('db_host')
        
        new_title = kwargs.get('title')
        new_description = kwargs.get('description')
        # new_logo_url = kwargs.get('logo_url')
        # new_text = kwargs.get('new_text')
        new_admin_email = kwargs.get('admin_email')
        
        # if not new_text and not new_title and not new_description and not new_logo_url and not new_admin_email:
        #     self.stderr.write("Error: Provide at least one of --new-text, --title, --description, --logo-url, or --admin-email.")
        #     return

        try:
            connection = mysql.connector.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_password
            )

            if connection.is_connected():
                self.stdout.write(f"Connected to the WordPress database {db_name}")

                cursor = connection.cursor()

                if new_title:
                    update_title_query = """
                    UPDATE wp_options
                    SET option_value = %s
                    WHERE option_name = 'blogname';
                    """
                    cursor.execute(update_title_query, (new_title,))

                if new_description:
                    update_description_query = """
                    UPDATE wp_options
                    SET option_value = %s
                    WHERE option_name = 'blogdescription';
                    """
                    cursor.execute(update_description_query, (new_description,))

                # if new_logo_url:
                #     update_logo_query = """
                #     UPDATE wp_options
                #     SET option_value = %s
                #     WHERE option_name = 'envo_royal_logo';
                #     """
                #     cursor.execute(update_logo_query, (new_logo_url,))
                

                # if new_text:
                #     keyword = "WE ARE YOUR SOLUTION"
                #     update_text_query = """
                #     UPDATE wp_posts
                #     SET post_content = REPLACE(post_content, %s, %s)
                #     WHERE post_content LIKE %s;
                #     """
                #     cursor.execute(update_text_query, (keyword, new_text, f"%{keyword}%"))

                #     rows_affected = cursor.rowcount
                #     if rows_affected > 0:
                #         self.stdout.write(self.style.SUCCESS(f"Text updated successfully in {rows_affected} posts"))
                #     else:
                #         self.stdout.write(self.style.WARNING(f"No posts found with '{keyword}' in post_content"))


                # user_id = 1
                
                if new_admin_email:
                    update_admin_email_query = """
                    UPDATE wp_options
                    SET option_value = %s
                    WHERE option_name = 'admin_email';
                    """
                    cursor.execute(update_admin_email_query, (new_admin_email,))
                    
                    
                    # update_user_email_query = """
                    # UPDATE wp_users
                    # SET user_email = %s
                    # WHERE ID = %s;
                    # """
                    # cursor.execute(update_user_email_query, (new_admin_email, user_id))
                    
                    # update_woocommerce_email_query = """
                    # UPDATE wp_options
                    # SET option_value = %s
                    # WHERE option_name IN ('woocommerce_email_from_address', 'woocommerce_stock_email_recipient');
                    # """
                    # cursor.execute(update_woocommerce_email_query, (new_admin_email,))

                    
                    # update_other_options_query = """
                    # UPDATE wp_options
                    # SET option_value = %s
                    # WHERE option_name IN ('auto_core_update_notified', 'fs_accounts', 'woocommerce_onboarding_profile', 'woocommerce_paypal_settings');
                    # """
                    # cursor.execute(update_other_options_query, (new_admin_email,))

                connection.commit()

                self.stdout.write(self.style.SUCCESS("WordPress site information updated successfully"))

        except Error as e:
            self.stderr.write(f"Error: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                self.stdout.write("MySQL connection is closed")
