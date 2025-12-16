import pymysql.cursors
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

DB_CONFIG = {
    'user': 'root',               
    'password': '',               
    'host': '127.0.0.1',          
    'database': 'rental_manager'  
}

DUE_DAY = 5
GRACE_PERIOD_DAYS = 5

def get_db_connection():
    conn = pymysql.connect(
        cursorclass=pymysql.cursors.DictCursor,
        **DB_CONFIG
    )
    return conn

def create_db():
    try:
        temp_config = DB_CONFIG.copy()
        db_name = temp_config.pop('database')
        conn = pymysql.connect(**temp_config)
        cursor = conn.cursor()        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        conn.select_db(db_name) 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                TenantID INT PRIMARY KEY AUTO_INCREMENT,
                FirstName VARCHAR(100) NOT NULL,
                LastName VARCHAR(100) NOT NULL,
                ContactNumber VARCHAR(20)         
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                PropertyID INT PRIMARY KEY AUTO_INCREMENT,
                Address VARCHAR(255) NOT NULL UNIQUE,
                MonthlyRent DECIMAL(10, 2) NOT NULL,
                TenantID INT,
                FOREIGN KEY (TenantID) REFERENCES tenants(TenantID)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rent_payments (
                PaymentID INT PRIMARY KEY AUTO_INCREMENT,
                PropertyID INT NOT NULL,
                AmountPaid DECIMAL(10, 2),
                ExpectedDueDate DATE NOT NULL,
                DatePaid DATE,
                PaymentStatus VARCHAR(10) NOT NULL,
                FOREIGN KEY (PropertyID) REFERENCES properties(PropertyID)
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM tenants")
        if cursor.fetchone()['COUNT(*)'] == 0:
            cursor.execute("INSERT INTO tenants (FirstName, LastName, ContactNumber) VALUES (%s, %s, %s)", ("Alice", "Smith", "555-0101"))
            cursor.execute("SELECT LAST_INSERT_ID() as id")
            tenant_id = cursor.fetchone()['id']            
            cursor.execute("INSERT INTO properties (Address, MonthlyRent, TenantID) VALUES (%s, %s, %s)", ("123 Main St", 1500.00, tenant_id))
        conn.commit()
        print("MySQL setup complete.")    
    except pymysql.err.OperationalError as e:
        print(f"\n--- ERROR CONNECTING TO MYSQL ---")
        print(f"Details: {e}")
        print("Please ensure XAMPP's MySQL server is running and configuration (root/no password) is correct.")
    except Exception as e:
        print(f"An unexpected error occurred during database setup: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
create_db()

def update_payment_status(payment_id, date_paid_str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ExpectedDueDate FROM rent_payments WHERE PaymentID = %s", (payment_id,))
    payment_record = cursor.fetchone()
    if not payment_record:
        conn.close()
        return
    expected_date = payment_record['ExpectedDueDate'] 
    paid_date = datetime.strptime(date_paid_str, '%Y-%m-%d').date()    
    late_threshold = expected_date.replace(day=DUE_DAY) + timedelta(days=GRACE_PERIOD_DAYS)
    if paid_date <= late_threshold:
        status = 'Paid'
    else:
        status = 'Late'
    cursor.execute("UPDATE rent_payments SET DatePaid = %s, PaymentStatus = %s WHERE PaymentID = %s", 
                   (paid_date.strftime('%Y-%m-%d'), status, payment_id))    
    conn.commit()
    conn.close()

def seed_monthly_payments():
    conn = get_db_connection()
    cursor = conn.cursor()    
    today = datetime.now().date()
    current_month_due_date = today.replace(day=DUE_DAY).strftime('%Y-%m-%d')
    cursor.execute("SELECT PropertyID, MonthlyRent FROM properties WHERE TenantID IS NOT NULL")
    properties = cursor.fetchall()

    for prop in properties:
        cursor.execute(
            "SELECT COUNT(*) FROM rent_payments WHERE PropertyID = %s AND ExpectedDueDate = %s",
            (prop['PropertyID'], current_month_due_date)
        )
        existing = cursor.fetchone()['COUNT(*)']

        if existing == 0:
            cursor.execute("""
                INSERT INTO rent_payments 
                (PropertyID, AmountPaid, ExpectedDueDate, PaymentStatus) 
                VALUES (%s, %s, %s, %s)
            """, (prop['PropertyID'], None, current_month_due_date, 'Due'))    
    conn.commit()
    conn.close()

def get_dashboard_data(month_filter=None):
    seed_monthly_payments()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if month_filter:
        today_month = month_filter
    else:
        today_month = datetime.now().strftime('%Y-%m')
        
    cursor.execute("""
        SELECT SUM(AmountPaid) AS TotalCollected
        FROM rent_payments 
        WHERE PaymentStatus IN ('Paid', 'Late') 
        AND DATE_FORMAT(ExpectedDueDate, '%%Y-%%m') = %s
    """, (today_month,))
    total_collected = cursor.fetchone()['TotalCollected'] or 0.0
    cursor.execute("SELECT COUNT(*) AS LateCount FROM rent_payments WHERE PaymentStatus = 'Late'")
    late_count = cursor.fetchone()['LateCount']
    cursor.execute("""
        SELECT 
            p.PropertyID, 
            p.Address, 
            p.MonthlyRent,
            p.TenantID,
            CONCAT(t.FirstName, ' ', t.LastName) AS TenantName,
            t.ContactNumber,
            -- Subquery 1 (Status)
            (SELECT PaymentStatus FROM rent_payments 
             WHERE PropertyID = p.PropertyID 
             AND DATE_FORMAT(ExpectedDueDate, '%%Y-%%m') = %s
             ORDER BY ExpectedDueDate DESC LIMIT 1) AS CurrentStatus,
            -- Subquery 2 (AmountPaid)
            (SELECT AmountPaid FROM rent_payments 
             WHERE PropertyID = p.PropertyID 
             AND DATE_FORMAT(ExpectedDueDate, '%%Y-%%m') = %s
             ORDER BY ExpectedDueDate DESC LIMIT 1) AS AmountPaid,
            -- Subquery 3 (DatePaid)
            (SELECT DatePaid FROM rent_payments 
             WHERE PropertyID = p.PropertyID 
             AND DATE_FORMAT(ExpectedDueDate, '%%Y-%%m') = %s
             ORDER BY ExpectedDueDate DESC LIMIT 1) AS DatePaid,
             -- Subquery 4 (PaymentID)
             (SELECT PaymentID FROM rent_payments 
             WHERE PropertyID = p.PropertyID 
             AND DATE_FORMAT(ExpectedDueDate, '%%Y-%%m') = %s
             ORDER BY ExpectedDueDate DESC LIMIT 1) AS CurrentPaymentID,
             -- Subquery 5 (ExpectedDueDate - for detail panel display)
             (SELECT ExpectedDueDate FROM rent_payments 
             WHERE PropertyID = p.PropertyID 
             AND DATE_FORMAT(ExpectedDueDate, '%%Y-%%m') = %s
             ORDER BY ExpectedDueDate DESC LIMIT 1) AS ExpectedDueDate
        FROM 
            properties p 
        LEFT JOIN 
            tenants t ON p.TenantID = t.TenantID
    """, (today_month, today_month, today_month, today_month, today_month))
    properties_data_rows = cursor.fetchall()        
    properties_data = []
    for row in properties_data_rows:
        data = dict(row)
        data['ExpectedDueDate'] = str(data['ExpectedDueDate']) if data['ExpectedDueDate'] else 'N/A'
        properties_data.append(data)
    tenants_list = get_all_tenants() 
    tenants_for_form = [{'TenantID': 0, 'Name': 'VACANT'}] + [{'TenantID': t['TenantID'], 'Name': f"{t['FirstName']} {t['LastName']}"} for t in tenants_list]
    conn.close()
    return total_collected, late_count, properties_data, tenants_for_form, today_month
    
def get_properties_data():
    conn = get_db_connection()
    cursor = conn.cursor()    
    cursor.execute("""
        SELECT 
            p.*, 
            CONCAT(t.FirstName, ' ', t.LastName) AS TenantName,
            t.ContactNumber AS ContactNumber 
        FROM 
            properties p 
        LEFT JOIN 
            tenants t ON p.TenantID = t.TenantID
    """)
    properties_data_rows = cursor.fetchall()
    properties = [dict(row) for row in properties_data_rows]
    cursor.execute("""
        SELECT
            PropertyID, 
            COUNT(PaymentID) AS LateCount
        FROM 
            rent_payments
        WHERE 
            PaymentStatus = 'Late'
        GROUP BY 
            PropertyID
    """)
    late_counts = cursor.fetchall()    
    late_counts_dict = {row['PropertyID']: row['LateCount'] for row in late_counts}
    cursor.execute("SELECT TenantID, FirstName, LastName FROM tenants")
    tenants = cursor.fetchall()
    tenants_list = [{'TenantID': t['TenantID'], 'Name': f"{t['FirstName']} {t['LastName']}"} for t in tenants]
    conn.close()
    return properties, late_counts_dict, tenants_list

def get_all_tenants():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TenantID, FirstName, LastName FROM tenants")
    tenants = cursor.fetchall()
    conn.close()
    return tenants

def reset_current_payment_status(property_id, due_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE rent_payments
        SET AmountPaid = NULL, 
            DatePaid = NULL, 
            PaymentStatus = 'Due'
        WHERE PropertyID = %s 
        AND DATE_FORMAT(ExpectedDueDate, '%%Y-%%m-%%d') = %s
    """, (property_id, due_date))    
    conn.commit()
    conn.close()

@app.route('/', defaults={'page': 'index'})
@app.route('/<page>', methods=['GET', 'POST'])
def single_page_app(page):
    
    current_month_ym = datetime.now().strftime('%Y-%m')    
    context = {
        'page': page, 
        'today': datetime.now().date().strftime('%Y-%m-%d'),
        'current_month_ym': current_month_ym 
    }
    
    if page == 'index':
        month_filter = request.args.get('month')         
        total_collected, late_count, properties_data, tenants_for_form, current_display_month = get_dashboard_data(month_filter)         
        context.update({
            'total_collected': total_collected,
            'late_count': late_count,
            'properties_data': properties_data,
            'tenants_for_form': tenants_for_form,
            'current_display_month': current_display_month
        })
    elif page == 'properties':
        properties, late_counts_dict, tenants_list = get_properties_data()
        context.update({
            'properties': properties,
            'late_counts_dict': late_counts_dict,
            'tenants_list': tenants_list
        })
    elif page == 'add_property':
        tenants = get_all_tenants()
        tenants_for_form = [{'TenantID': 0, 'Name': 'VACANT'}] + [{'TenantID': t['TenantID'], 'Name': f"{t['FirstName']} {t['LastName']}"} for t in tenants]
        context.update({'tenants': tenants_for_form})    
    return render_template('single_page.html', **context)

@app.route('/record_payment/<int:payment_id>', methods=('POST',))
def record_payment(payment_id):
    date_paid = request.form['date_paid']
    amount_paid = float(request.form['amount_paid'])    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE rent_payments SET AmountPaid = %s WHERE PaymentID = %s", (amount_paid, payment_id))
    conn.commit()
    conn.close()
    update_payment_status(payment_id, date_paid)
    return redirect(url_for('single_page_app', page='index'))

@app.route('/assign_tenant_post/<int:property_id>', methods=('POST',))
def assign_tenant_post(property_id):
    conn = get_db_connection()
    cursor = conn.cursor()    
    new_tenant_id = request.form['tenant_id']
    start_month = request.form['start_month']     
    tenant_id_to_assign = int(new_tenant_id) if new_tenant_id != '0' else None
    cursor.execute("""
        UPDATE properties 
        SET TenantID = %s 
        WHERE PropertyID = %s
    """, (tenant_id_to_assign, property_id))    
    conn.commit()
    
    if tenant_id_to_assign is not None and start_month:
        try:
            due_date = datetime.strptime(start_month, '%Y-%m').date().replace(day=DUE_DAY).strftime('%Y-%m-%d')            
            cursor.execute(
                "SELECT COUNT(*) FROM rent_payments WHERE PropertyID = %s AND ExpectedDueDate = %s",
                (property_id, due_date)
            )
            existing = cursor.fetchone()['COUNT(*)']
            if existing == 0:
                cursor.execute("""
                    INSERT INTO rent_payments 
                    (PropertyID, AmountPaid, ExpectedDueDate, PaymentStatus) 
                    VALUES (%s, %s, %s, %s)
                """, (property_id, None, due_date, 'Due'))
                conn.commit()            
        except Exception as e:
            print(f"Error creating initial payment record: {e}")
    conn.close()    
    return redirect(url_for('single_page_app', page='properties'))

@app.route('/manage_property_post', methods=('POST',))
def manage_property_post():
    action = request.form['action']
    property_id = request.form['property_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if action == 'update':
        address = request.form['address']
        monthly_rent = float(request.form['monthly_rent'])        
        try:
            cursor.execute("""
                UPDATE properties 
                SET Address = %s, MonthlyRent = %s 
                WHERE PropertyID = %s
            """, (address, monthly_rent, property_id))
            conn.commit()
        except pymysql.err.IntegrityError:
            pass

    elif action == 'delete':
        cursor.execute("DELETE FROM rent_payments WHERE PropertyID = %s", (property_id,))
        cursor.execute("UPDATE properties SET TenantID = NULL WHERE PropertyID = %s", (property_id,))
        cursor.execute("DELETE FROM properties WHERE PropertyID = %s", (property_id,))
        conn.commit()            
    conn.close()   
    return redirect(url_for('single_page_app', page='properties'))

@app.route('/add_property_post', methods=('POST',))
def add_property_post():
    address = request.form['address']
    monthly_rent = float(request.form['monthly_rent'])
    tenant_id = request.form.get('tenant_id')        
    tenant_id_to_assign = int(tenant_id) if tenant_id and tenant_id != '0' else None
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO properties (Address, MonthlyRent, TenantID) VALUES (%s, %s, %s)", 
                     (address, monthly_rent, tenant_id_to_assign))
        conn.commit()
    except pymysql.err.IntegrityError:
        pass
    finally:
        conn.close()
        return redirect(url_for('single_page_app', page='properties'))

@app.route('/manage_tenant_post', methods=('POST',))
def manage_tenant_post():
    action = request.form['action']
    conn = get_db_connection()
    cursor = conn.cursor()    
    if action == 'add':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        contact_number = request.form['contact_number']
        cursor.execute("INSERT INTO tenants (FirstName, LastName, ContactNumber) VALUES (%s, %s, %s)", 
                     (first_name, last_name, contact_number))
        conn.commit()
        
    elif action == 'delete':
        tenant_id = request.form['tenant_id']
        current_month_due_date = datetime.now().date().replace(day=DUE_DAY).strftime('%Y-%m-%d')
        cursor.execute("SELECT PropertyID FROM properties WHERE TenantID = %s", (tenant_id,))
        properties_to_reset = cursor.fetchall()
        for prop in properties_to_reset:
            reset_current_payment_status(prop['PropertyID'], current_month_due_date)
        cursor.execute("UPDATE properties SET TenantID = NULL WHERE TenantID = %s", (tenant_id,))
        conn.commit()
        cursor.execute("DELETE FROM tenants WHERE TenantID = %s", (tenant_id,))
        conn.commit()       
    conn.close()   
    return redirect(url_for('single_page_app', page='properties'))

if __name__ == '__main__':
    app.run(debug=True)